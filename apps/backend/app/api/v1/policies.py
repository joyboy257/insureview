from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.policy import Policy, Benefit, Rider, Exclusion
from app.schemas.policy import PolicySummary, PolicyDetail

router = APIRouter()


@router.get("", response_model=list[PolicySummary])
async def list_policies(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Policy)
        .where(Policy.user_id == current_user.id)
        .order_by(Policy.created_at.desc())
    )
    policies = result.scalars().all()
    return policies


@router.get("/{policy_id}", response_model=PolicyDetail)
async def get_policy(
    policy_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Policy)
        .options(selectinload(Policy.benefits), selectinload(Policy.riders), selectinload(Policy.exclusions))
        .where(Policy.id == policy_id, Policy.user_id == current_user.id)
    )
    policy = result.scalar_one_or_none()
    if not policy:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Policy not found")
    return policy


@router.delete("/{policy_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_policy(
    policy_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Policy).where(Policy.id == policy_id, Policy.user_id == current_user.id)
    )
    policy = result.scalar_one_or_none()
    if not policy:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Policy not found")
    await db.delete(policy)
    await db.commit()
