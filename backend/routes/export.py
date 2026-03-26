"""Export API routes for dataset download."""

import csv
import io
import json
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_db
from models.evaluation import Evaluation
from routes.auth import verify_token

router = APIRouter(prefix="/api", tags=["export"])


@router.get("/export/json")
async def export_json(
    accuracy: str = Query(None),
    severity: str = Query(None),
    db: AsyncSession = Depends(get_db),
    _token: str = Depends(verify_token),
):
    """Export evaluations as JSON file."""
    query = select(Evaluation).order_by(desc(Evaluation.created_at))
    if accuracy:
        query = query.where(Evaluation.accuracy == accuracy)
    if severity:
        query = query.where(Evaluation.severity == severity)

    result = await db.execute(query)
    evaluations = result.scalars().all()

    data = [e.to_dict() for e in evaluations]
    content = json.dumps(data, indent=2, default=str)

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"evalflow_export_{timestamp}.json"

    return StreamingResponse(
        io.BytesIO(content.encode("utf-8")),
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get("/export/csv")
async def export_csv(
    accuracy: str = Query(None),
    severity: str = Query(None),
    db: AsyncSession = Depends(get_db),
    _token: str = Depends(verify_token),
):
    """Export evaluations as CSV file."""
    query = select(Evaluation).order_by(desc(Evaluation.created_at))
    if accuracy:
        query = query.where(Evaluation.accuracy == accuracy)
    if severity:
        query = query.where(Evaluation.severity == severity)

    result = await db.execute(query)
    evaluations = result.scalars().all()

    output = io.StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow([
        "id", "prompt", "response", "accuracy", "issues",
        "confidence", "severity", "llm_score", "rule_score",
        "final_score", "latency_ms", "created_at",
    ])

    # Data
    for e in evaluations:
        writer.writerow([
            e.id,
            e.prompt,
            e.response,
            e.accuracy,
            "|".join(e.issues_list),
            e.confidence,
            e.severity,
            e.llm_score,
            e.rule_score,
            e.final_score,
            e.latency_ms,
            e.created_at.isoformat() if e.created_at else "",
        ])

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"evalflow_export_{timestamp}.csv"

    return StreamingResponse(
        io.BytesIO(output.getvalue().encode("utf-8")),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
