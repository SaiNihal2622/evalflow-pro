"""Statistics and analytics API routes."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_db
from models.evaluation import StatsResponse, TrendsResponse, IssueDistributionResponse
from routes.auth import verify_token
from services.analytics import analytics_service

router = APIRouter(prefix="/api", tags=["analytics"])


@router.get("/stats", response_model=StatsResponse)
async def get_stats(
    db: AsyncSession = Depends(get_db),
    _token: str = Depends(verify_token),
):
    """Get dashboard overview statistics."""
    return await analytics_service.get_stats(db)


@router.get("/analytics/trends", response_model=TrendsResponse)
async def get_trends(
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    _token: str = Depends(verify_token),
):
    """Get evaluation trends over time."""
    return await analytics_service.get_trends(db, days=days)


@router.get("/analytics/issues", response_model=IssueDistributionResponse)
async def get_issue_distribution(
    db: AsyncSession = Depends(get_db),
    _token: str = Depends(verify_token),
):
    """Get distribution of issue types."""
    return await analytics_service.get_issue_distribution(db)
