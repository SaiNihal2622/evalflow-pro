"""Evaluation orchestration service.

Combines LLM evaluation with rule engine for comprehensive scoring.
"""

import asyncio
import json
import logging
import time
from typing import List, Optional

from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from llm import get_provider
from models.evaluation import Evaluation, EvaluationRequest, EvaluationResult
from services.rule_engine import rule_engine

logger = logging.getLogger(__name__)

# Score weights
LLM_WEIGHT = 0.6
RULE_WEIGHT = 0.4


class EvaluationService:
    """Orchestrates the full evaluation pipeline."""

    def __init__(self):
        try:
            self.llm_provider = get_provider()
        except Exception as e:
            logger.warning(f"Failed to initialize LLM provider: {e}. Running in rules-only mode.")
            self.llm_provider = None

    async def evaluate_single(
        self, request: EvaluationRequest, db: AsyncSession
    ) -> EvaluationResult:
        """Evaluate a single prompt-response pair."""
        start_time = time.time()

        # Run LLM evaluation
        llm_result = None
        llm_score = None
        if self.llm_provider:
            try:
                llm_result = await self.llm_provider.evaluate(request.prompt, request.response)
                llm_score = self._calculate_llm_score(llm_result)
            except Exception as e:
                logger.error(f"LLM evaluation failed: {e}")
                llm_result = None

        # Run rule engine (always runs)
        rule_result = rule_engine.evaluate(request.prompt, request.response)

        # Combine results
        combined = self._combine_results(llm_result, rule_result)

        # Calculate final score
        if llm_score is not None:
            final_score = (llm_score * LLM_WEIGHT) + (rule_result.rule_score * RULE_WEIGHT)
        else:
            final_score = rule_result.rule_score  # Rules-only mode

        latency_ms = int((time.time() - start_time) * 1000)

        # Store in database
        evaluation = Evaluation(
            prompt=request.prompt,
            response=request.response,
            accuracy=combined["accuracy"],
            issues=json.dumps(combined["issues"]),
            confidence=combined["confidence"],
            severity=combined["severity"],
            llm_score=llm_score,
            rule_score=rule_result.rule_score,
            final_score=round(final_score, 4),
            latency_ms=latency_ms,
        )
        db.add(evaluation)
        await db.flush()
        await db.refresh(evaluation)

        logger.info(
            f"Evaluation #{evaluation.id}: accuracy={combined['accuracy']}, "
            f"final_score={final_score:.4f}, latency={latency_ms}ms"
        )

        return EvaluationResult(
            id=evaluation.id,
            prompt=evaluation.prompt,
            response=evaluation.response,
            accuracy=evaluation.accuracy,
            issues=combined["issues"],
            confidence=evaluation.confidence,
            severity=evaluation.severity,
            llm_score=evaluation.llm_score,
            rule_score=evaluation.rule_score,
            final_score=evaluation.final_score,
            latency_ms=evaluation.latency_ms,
            created_at=evaluation.created_at.isoformat() if evaluation.created_at else None,
        )

    async def evaluate_batch(
        self, requests: List[EvaluationRequest], db: AsyncSession, max_concurrent: int = 5
    ) -> List[EvaluationResult]:
        """Evaluate multiple prompt-response pairs with concurrency control."""
        semaphore = asyncio.Semaphore(max_concurrent)
        results = []

        async def eval_with_semaphore(req: EvaluationRequest) -> EvaluationResult:
            async with semaphore:
                return await self.evaluate_single(req, db)

        tasks = [eval_with_semaphore(req) for req in requests]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out exceptions
        valid_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Batch evaluation item {i} failed: {result}")
            else:
                valid_results.append(result)

        return valid_results

    async def get_evaluations(
        self,
        db: AsyncSession,
        page: int = 1,
        page_size: int = 20,
        accuracy_filter: Optional[str] = None,
        severity_filter: Optional[str] = None,
        search: Optional[str] = None,
    ):
        """Retrieve paginated evaluations with optional filters."""
        query = select(Evaluation)

        if accuracy_filter:
            query = query.where(Evaluation.accuracy == accuracy_filter)
        if severity_filter:
            query = query.where(Evaluation.severity == severity_filter)
        if search:
            query = query.where(
                Evaluation.prompt.ilike(f"%{search}%") | Evaluation.response.ilike(f"%{search}%")
            )

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        # Paginate
        offset = (page - 1) * page_size
        query = query.order_by(desc(Evaluation.created_at)).offset(offset).limit(page_size)
        result = await db.execute(query)
        evaluations = result.scalars().all()

        items = [
            EvaluationResult(
                id=e.id,
                prompt=e.prompt,
                response=e.response,
                accuracy=e.accuracy,
                issues=e.issues_list,
                confidence=e.confidence,
                severity=e.severity,
                llm_score=e.llm_score,
                rule_score=e.rule_score,
                final_score=e.final_score,
                latency_ms=e.latency_ms,
                created_at=e.created_at.isoformat() if e.created_at else None,
            )
            for e in evaluations
        ]

        total_pages = (total + page_size - 1) // page_size

        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
        }

    async def get_evaluation_by_id(self, eval_id: int, db: AsyncSession) -> Optional[EvaluationResult]:
        """Get a single evaluation by ID."""
        result = await db.execute(select(Evaluation).where(Evaluation.id == eval_id))
        e = result.scalar_one_or_none()
        if not e:
            return None
        return EvaluationResult(
            id=e.id,
            prompt=e.prompt,
            response=e.response,
            accuracy=e.accuracy,
            issues=e.issues_list,
            confidence=e.confidence,
            severity=e.severity,
            llm_score=e.llm_score,
            rule_score=e.rule_score,
            final_score=e.final_score,
            latency_ms=e.latency_ms,
            created_at=e.created_at.isoformat() if e.created_at else None,
        )

    async def delete_evaluation(self, eval_id: int, db: AsyncSession) -> bool:
        """Delete an evaluation by ID."""
        result = await db.execute(select(Evaluation).where(Evaluation.id == eval_id))
        evaluation = result.scalar_one_or_none()
        if not evaluation:
            return False
        await db.delete(evaluation)
        return True

    def _calculate_llm_score(self, llm_result: dict) -> float:
        """Convert LLM result to a numeric score."""
        score = 1.0

        accuracy = llm_result.get("accuracy", "unknown")
        if accuracy in ("incorrect", "unknown"):
            score -= 0.5  # heavy penalty for wrong/unknown answers

        issues = llm_result.get("issues", [])
        score -= len(issues) * 0.15  # each issue costs 15%

        severity = llm_result.get("severity", "medium")
        if severity == "high":
            score -= 0.2
        elif severity == "medium":
            score -= 0.05

        return max(0.0, min(1.0, score))

    def _combine_results(self, llm_result: Optional[dict], rule_result) -> dict:
        """Combine LLM and rule engine results into a single evaluation."""
        if llm_result:
            # Merge issues from both sources (deduplicated)
            llm_issues = set(llm_result.get("issues", []))
            rule_issues = set(rule_result.issues)
            all_issues = list(llm_issues | rule_issues)

            # Accuracy: treat 'unknown' as 'incorrect' if there are any issues
            accuracy = llm_result.get("accuracy", "unknown")
            if accuracy == "unknown":
                accuracy = "incorrect" if len(all_issues) > 0 else "correct"
            if rule_result.rule_score < 0.3:
                accuracy = "incorrect"

            # Confidence from LLM, reduced if rule engine found problems
            confidence = llm_result.get("confidence", 0.5)
            if rule_result.rule_score < 0.5:
                confidence = min(confidence, rule_result.rule_score)
            if accuracy == "incorrect" and confidence > 0.5:
                confidence = max(0.1, confidence * 0.5)  # reduce overconfidence on wrong answers

            # Severity: worst of both
            llm_severity = llm_result.get("severity", "medium")
            rule_severity = "high" if rule_result.rule_score < 0.3 else "medium" if rule_result.rule_score < 0.6 else "low"
            severity = self._worst_severity(llm_severity, rule_severity)
            if accuracy == "incorrect" and severity == "low":
                severity = "medium"  # incorrect answers should never be 'low' severity
        else:
            # Rules-only mode
            all_issues = rule_result.issues
            accuracy = "incorrect" if rule_result.rule_score < 0.5 else "correct"
            confidence = rule_result.rule_score
            severity = "high" if rule_result.rule_score < 0.3 else "medium" if rule_result.rule_score < 0.6 else "low"

        return {
            "accuracy": accuracy,
            "issues": all_issues,
            "confidence": round(confidence, 4),
            "severity": severity,
        }

    def _worst_severity(self, a: str, b: str) -> str:
        """Return the more severe of two severity levels."""
        order = {"low": 0, "medium": 1, "high": 2}
        return a if order.get(a, 1) >= order.get(b, 1) else b


# Singleton
evaluation_service = EvaluationService()
