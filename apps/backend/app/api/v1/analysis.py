from uuid import UUID
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.config import settings
from app.core.security import get_mas_disclaimer
from app.models.user import User
from app.models.session import AnalysisResult
from app.schemas.analysis import AnalysisResponse, AnalysisOutputSchema, AnalysisRequest

router = APIRouter()


@router.post("", response_model=AnalysisResponse)
async def trigger_analysis(
    req: AnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from app.workers.analysis_worker import trigger_analysis_job
    analysis_id = trigger_analysis_job(str(current_user.id), [str(p) for p in (req.policy_ids or [])])

    result = await db.execute(
        select(AnalysisResult).where(AnalysisResult.id == analysis_id)
    )
    record = result.scalar_one_or_none()

    if not record:
        return AnalysisResponse(
            data=AnalysisOutputSchema(),
            mas_disclaimer=get_mas_disclaimer(),
            generated_at=datetime.now(timezone.utc),
            disclaimer_version=settings.mas_disclaimer_version,
        )

    return AnalysisResponse(
        data=record.output_data,
        mas_disclaimer=get_mas_disclaimer(),
        generated_at=record.created_at,
        disclaimer_version=settings.mas_disclaimer_version,
    )


@router.get("", response_model=AnalysisResponse | None)
async def get_latest_analysis(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Fetch the most recent analysis result for the current user."""
    result = await db.execute(
        select(AnalysisResult)
        .where(AnalysisResult.user_id == current_user.id)
        .order_by(AnalysisResult.created_at.desc())
        .limit(1)
    )
    record = result.scalar_one_or_none()
    if not record:
        return None

    return AnalysisResponse(
        data=record.output_data or {},
        mas_disclaimer=get_mas_disclaimer(),
        generated_at=record.created_at,
        disclaimer_version=settings.mas_disclaimer_version,
    )


@router.get("/{analysis_id}", response_model=AnalysisResponse)
async def get_analysis(
    analysis_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(AnalysisResult).where(
            AnalysisResult.id == analysis_id,
            AnalysisResult.user_id == current_user.id,
        )
    )
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis not found")

    return AnalysisResponse(
        data=record.output_data,
        mas_disclaimer=get_mas_disclaimer(),
        generated_at=record.created_at,
        disclaimer_version=settings.mas_disclaimer_version,
    )
