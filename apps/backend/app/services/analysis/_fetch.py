"""
Shared policy-fetching helpers for the analysis engine.

Provides `get_user_policies_with_relations` which loads all active policies
for a user with their benefits, riders, and exclusions eagerly loaded.
"""

import uuid
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import async_session_maker
from app.models.policy import Policy, Benefit, Rider, Exclusion


async def get_user_policies_with_relations(
    user_id: uuid.UUID,
    policy_ids: list[str] | None = None,
) -> Sequence[Policy]:
    """
    Fetch active policies for a user with all related benefits, riders, exclusions.

    If policy_ids is provided, only those policies are included.
    """
    async with async_session_maker() as db:
        query = (
            select(Policy)
            .options(
                selectinload(Policy.benefits),
                selectinload(Policy.riders),
                selectinload(Policy.exclusions),
            )
            .where(Policy.user_id == user_id)
            .where(Policy.policy_status == "active")
        )
        if policy_ids:
            pids = [uuid.UUID(pid) for pid in policy_ids]
            query = query.where(Policy.id.in_(pids))

        result = await db.execute(query)
        return result.scalars().all()
