"""Evaluation API routes."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_db
from models.evaluation import (
    EvaluationRequest,
    BatchEvaluationRequest,
    EvaluationResult,
    PaginatedEvaluations,
)
from routes.auth import verify_token
from services.evaluation import evaluation_service

router = APIRouter(prefix="/api", tags=["evaluations"])


@router.post("/evaluate", response_model=EvaluationResult)
async def evaluate(
    request: EvaluationRequest,
    db: AsyncSession = Depends(get_db),
    _token: str = Depends(verify_token),
):
    """Evaluate a single prompt-response pair."""
    try:
        result = await evaluation_service.evaluate_single(request, db)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")


@router.post("/batch-evaluate", response_model=list[EvaluationResult])
async def batch_evaluate(
    request: BatchEvaluationRequest,
    db: AsyncSession = Depends(get_db),
    _token: str = Depends(verify_token),
):
    """Evaluate multiple prompt-response pairs in batch."""
    try:
        results = await evaluation_service.evaluate_batch(request.evaluations, db)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch evaluation failed: {str(e)}")


@router.get("/evaluations", response_model=PaginatedEvaluations)
async def list_evaluations(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    accuracy: str = Query(None, description="Filter by accuracy: correct, incorrect"),
    severity: str = Query(None, description="Filter by severity: low, medium, high"),
    search: str = Query(None, description="Search in prompt/response text"),
    db: AsyncSession = Depends(get_db),
    _token: str = Depends(verify_token),
):
    """Get paginated list of evaluations with optional filters."""
    result = await evaluation_service.get_evaluations(
        db, page=page, page_size=page_size,
        accuracy_filter=accuracy, severity_filter=severity, search=search,
    )
    return result


@router.get("/evaluations/{eval_id}", response_model=EvaluationResult)
async def get_evaluation(
    eval_id: int,
    db: AsyncSession = Depends(get_db),
    _token: str = Depends(verify_token),
):
    """Get a single evaluation by ID."""
    result = await evaluation_service.get_evaluation_by_id(eval_id, db)
    if not result:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    return result


@router.delete("/evaluations/{eval_id}")
async def delete_evaluation(
    eval_id: int,
    db: AsyncSession = Depends(get_db),
    _token: str = Depends(verify_token),
):
    """Delete an evaluation by ID."""
    deleted = await evaluation_service.delete_evaluation(eval_id, db)
    if not deleted:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    return {"message": "Evaluation deleted", "id": eval_id}
