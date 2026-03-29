from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.security import get_mas_disclaimer
from app.models.user import User
from app.models.session import ParsingSession, ConsentRecord
from app.schemas.upload import PresignedUrlRequest, PresignedUrlResponse
from app.services.storage.s3_client import generate_presigned_upload_url

router = APIRouter()


async def require_pdpa_consent(user_id: str, db: AsyncSession) -> None:
    result = await db.execute(
        select(ConsentRecord)
        .where(
            ConsentRecord.user_id == user_id,
            ConsentRecord.consent_type.in_(["pdpa_upload", "vault_optin"]),
            ConsentRecord.withdrawn_at.is_(None),
        )
        .order_by(ConsentRecord.given_at.desc())
    )
    latest = result.scalar_one_or_none()
    if not latest:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="PDPA consent required before uploading documents",
        )
    one_year_ago = datetime.now(timezone.utc) - timedelta(days=365)
    if latest.given_at < one_year_ago:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Consent expired. Please re-agree to the Privacy Policy.",
        )


@router.post("/presigned-url", response_model=PresignedUrlResponse)
async def get_upload_url(
    req: PresignedUrlRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_pdpa_consent(str(current_user.id), db)

    if not req.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only PDF files are accepted")

    if req.file_size_bytes > 52_428_800:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File exceeds 50MB limit")

    upload_url, s3_key = generate_presigned_upload_url(req.filename, current_user.id)
    expires_at = datetime.now(timezone.utc) + timedelta(hours=1)

    session = ParsingSession(
        user_id=current_user.id,
        original_filename=req.filename,
        file_size_bytes=req.file_size_bytes,
        s3_upload_key=s3_key,
        s3_upload_url=upload_url,
        parse_status="pending",
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)

    return PresignedUrlResponse(
        upload_url=upload_url,
        s3_key=s3_key,
        expires_at=expires_at,
    )


@router.post("/complete-upload/{session_id}")
async def complete_upload(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from app.workers.parse_worker import trigger_parse_job
    result = await db.execute(
        select(ParsingSession).where(
            ParsingSession.id == session_id,
            ParsingSession.user_id == current_user.id,
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    session.parse_status = "processing"
    await db.commit()

    trigger_parse_job(str(session.id))
    return {"status": "processing", "session_id": str(session.id)}
