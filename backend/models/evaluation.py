"""Evaluation SQLAlchemy model and Pydantic schemas."""

import json
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, func

from db.database import Base


# ─── SQLAlchemy Model ───────────────────────────────────────────────


class Evaluation(Base):
    __tablename__ = "evaluations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    prompt = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    accuracy = Column(String(20), nullable=False, default="unknown")
    issues = Column(Text, nullable=False, default="[]")  # JSON array
    confidence = Column(Float, nullable=False, default=0.0)
    severity = Column(String(10), nullable=False, default="low")
    llm_score = Column(Float, nullable=True)
    rule_score = Column(Float, nullable=True)
    final_score = Column(Float, nullable=True)
    latency_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    @property
    def issues_list(self) -> list:
        try:
            return json.loads(self.issues)
        except (json.JSONDecodeError, TypeError):
            return []

    @issues_list.setter
    def issues_list(self, value: list):
        self.issues = json.dumps(value)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "prompt": self.prompt,
            "response": self.response,
            "accuracy": self.accuracy,
            "issues": self.issues_list,
            "confidence": self.confidence,
            "severity": self.severity,
            "llm_score": self.llm_score,
            "rule_score": self.rule_score,
            "final_score": self.final_score,
            "latency_ms": self.latency_ms,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


# ─── Pydantic Schemas ──────────────────────────────────────────────


class EvaluationRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=10000, description="The input prompt")
    response: str = Field(..., min_length=1, max_length=50000, description="The LLM response to evaluate")


class BatchEvaluationRequest(BaseModel):
    evaluations: List[EvaluationRequest] = Field(..., min_length=1, max_length=100)


class EvaluationResult(BaseModel):
    id: int
    prompt: str
    response: str
    accuracy: str
    issues: List[str]
    confidence: float
    severity: str
    llm_score: Optional[float] = None
    rule_score: Optional[float] = None
    final_score: Optional[float] = None
    latency_ms: Optional[int] = None
    created_at: Optional[str] = None


class PaginatedEvaluations(BaseModel):
    items: List[EvaluationResult]
    total: int
    page: int
    page_size: int
    total_pages: int


class StatsResponse(BaseModel):
    total_evaluations: int = 0
    correct_count: int = 0
    incorrect_count: int = 0
    accuracy_rate: float = 0.0
    avg_confidence: float = 0.0
    avg_final_score: float = 0.0
    issue_distribution: dict = {}
    severity_distribution: dict = {}
    recent_evaluations: List[EvaluationResult] = []


class TrendDataPoint(BaseModel):
    date: str
    total: int
    correct: int
    incorrect: int
    avg_confidence: float


class TrendsResponse(BaseModel):
    trends: List[TrendDataPoint]


class IssueDistribution(BaseModel):
    issue: str
    count: int
    percentage: float


class IssueDistributionResponse(BaseModel):
    issues: List[IssueDistribution]
    total_issues: int
