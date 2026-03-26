"""Analytics service for aggregating evaluation data."""

import json
import logging
from collections import Counter
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import select, func, case, cast, Date
from sqlalchemy.ext.asyncio import AsyncSession

from models.evaluation import (
    Evaluation,
    EvaluationResult,
    StatsResponse,
    TrendDataPoint,
    TrendsResponse,
    IssueDistribution,
    IssueDistributionResponse,
)

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Aggregation queries for dashboard statistics."""

    async def get_stats(self, db: AsyncSession) -> StatsResponse:
        """Get dashboard overview statistics."""
        # Total count
        total_result = await db.execute(select(func.count(Evaluation.id)))
        total = total_result.scalar() or 0

        if total == 0:
            return StatsResponse()

        # Accuracy counts
        correct_result = await db.execute(
            select(func.count(Evaluation.id)).where(Evaluation.accuracy == "correct")
        )
        correct_count = correct_result.scalar() or 0

        incorrect_result = await db.execute(
            select(func.count(Evaluation.id)).where(Evaluation.accuracy == "incorrect")
        )
        incorrect_count = incorrect_result.scalar() or 0

        # Averages
        avg_result = await db.execute(
            select(
                func.avg(Evaluation.confidence),
                func.avg(Evaluation.final_score),
            )
        )
        row = avg_result.one()
        avg_confidence = round(float(row[0] or 0), 4)
        avg_final_score = round(float(row[1] or 0), 4)

        # Issue distribution — need to parse JSON from each row
        all_evals = await db.execute(select(Evaluation.issues))
        issue_counter = Counter()
        for (issues_json,) in all_evals:
            try:
                issues = json.loads(issues_json) if issues_json else []
                issue_counter.update(issues)
            except (json.JSONDecodeError, TypeError):
                pass

        # Severity distribution
        severity_result = await db.execute(
            select(Evaluation.severity, func.count(Evaluation.id)).group_by(Evaluation.severity)
        )
        severity_distribution = {row[0]: row[1] for row in severity_result}

        # Recent evaluations
        recent_result = await db.execute(
            select(Evaluation).order_by(Evaluation.created_at.desc()).limit(5)
        )
        recent_evals = recent_result.scalars().all()
        recent = [
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
            for e in recent_evals
        ]

        accuracy_rate = round(correct_count / total, 4) if total > 0 else 0.0

        return StatsResponse(
            total_evaluations=total,
            correct_count=correct_count,
            incorrect_count=incorrect_count,
            accuracy_rate=accuracy_rate,
            avg_confidence=avg_confidence,
            avg_final_score=avg_final_score,
            issue_distribution=dict(issue_counter),
            severity_distribution=severity_distribution,
            recent_evaluations=recent,
        )

    async def get_trends(self, db: AsyncSession, days: int = 30) -> TrendsResponse:
        """Get evaluation trends over time."""
        cutoff = datetime.utcnow() - timedelta(days=days)

        result = await db.execute(
            select(
                cast(Evaluation.created_at, Date).label("date"),
                func.count(Evaluation.id).label("total"),
                func.sum(case((Evaluation.accuracy == "correct", 1), else_=0)).label("correct"),
                func.sum(case((Evaluation.accuracy == "incorrect", 1), else_=0)).label("incorrect"),
                func.avg(Evaluation.confidence).label("avg_confidence"),
            )
            .where(Evaluation.created_at >= cutoff)
            .group_by(cast(Evaluation.created_at, Date))
            .order_by(cast(Evaluation.created_at, Date))
        )

        trends = []
        for row in result:
            trends.append(
                TrendDataPoint(
                    date=str(row.date),
                    total=row.total,
                    correct=row.correct or 0,
                    incorrect=row.incorrect or 0,
                    avg_confidence=round(float(row.avg_confidence or 0), 4),
                )
            )

        return TrendsResponse(trends=trends)

    async def get_issue_distribution(self, db: AsyncSession) -> IssueDistributionResponse:
        """Get distribution of issue types across all evaluations."""
        all_evals = await db.execute(select(Evaluation.issues))
        issue_counter = Counter()
        for (issues_json,) in all_evals:
            try:
                issues = json.loads(issues_json) if issues_json else []
                issue_counter.update(issues)
            except (json.JSONDecodeError, TypeError):
                pass

        total_issues = sum(issue_counter.values())
        issues = [
            IssueDistribution(
                issue=issue,
                count=count,
                percentage=round(count / total_issues * 100, 2) if total_issues > 0 else 0,
            )
            for issue, count in issue_counter.most_common()
        ]

        return IssueDistributionResponse(issues=issues, total_issues=total_issues)


# Singleton
analytics_service = AnalyticsService()
