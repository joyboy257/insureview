from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.session import ParsingSession

router = APIRouter()


@router.get("/{session_id}")
async def get_parsing_status(
    session_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ParsingSession).where(
            ParsingSession.id == session_id,
            ParsingSession.user_id == current_user.id,
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    return {
        "id": str(session.id),
        "status": session.parse_status,
        "original_filename": session.original_filename,
        "document_type": session.document_type,
        "parse_error": session.parse_error,
        "parse_confidence": None,
        "completed_at": session.completed_at,
    }
