import uuid
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import hash_email
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.session import ConsentRecord

router = APIRouter()


@router.post("/magic-link")
async def request_magic_link(
    email: str,
    db: AsyncSession = Depends(get_db),
):
    hashed = hash_email(email)
    result = await db.execute(select(User).where(User.hashed_email == hashed))
    user = result.scalar_one_or_none()

    if not user:
        user = User(hashed_email=hashed)
        db.add(user)
        await db.commit()
        await db.refresh(user)

    token = str(uuid.uuid4())
    user.magic_link_token = token
    user.magic_link_expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)
    await db.commit()

    magic_link = f"{'http://localhost:3000'}/api/auth/callback?token={token}"
    return {"message": "Magic link sent", "magic_link": magic_link}


@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "full_name": current_user.full_name,
        "agreed_to_pdpa_at": current_user.agreed_to_pdpa_at,
    }


@router.post("/verify-token")
async def verify_session(current_user: User = Depends(get_current_user)):
    return {"user_id": str(current_user.id), "active": current_user.is_active}
