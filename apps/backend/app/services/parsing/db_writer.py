"""
DB writer for parsed policy data.

Writes a validated ParsedPolicy to the database, creating Policy,
Benefit, Rider, and Exclusion records within a transaction.
"""

import logging
import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import select_result_scala

from app.core.database import get_db
from app.models.policy import Benefit, Exclusion, Policy, Rider
from app.models.session import ParsingSession
from app.services.parsing.output_parser import ParsedPolicy

logger = logging.getLogger(__name__)


async def write_parsed_policy(parsed: ParsedPolicy, session_id: str) -> Policy:
    """
    Write a ParsedPolicy to the database and update the ParsingSession.

    Creates:
      - 1 Policy record
      - N Benefit records
      - N Rider records
      - N Exclusion records

    Updates ParsingSession.parse_status to 'completed'.

    Returns the created Policy record.
    """
    session_uuid = uuid.UUID(session_id)

    async for db in get_db():
        # Fetch the parsing session to get user_id
        result = await db.execute(
            select(ParsingSession).where(ParsingSession.id == session_uuid)
        )
        parsing_session: ParsingSession | None = result.scalar_one_or_none()

        if not parsing_session:
            raise ValueError(f"ParsingSession {session_id} not found")

        user_id = parsing_session.user_id

        # Create Policy
        policy = Policy(
            user_id=user_id,
            insurer_code=parsed.insurer_code,
            insurer_name=parsed.insurer_name,
            product_name=parsed.product_name,
            product_type=parsed.product_type,
            policy_number=parsed.policy_number,
            issue_date=parsed.issue_date,
            expiry_date=parsed.expiry_date,
            sum_assured_cents=parsed.sum_assured_cents,
            premium_amount_cents=parsed.premium_amount_cents,
            premium_frequency=parsed.premium_frequency,
            currency=parsed.currency,
            policy_status=parsed.policy_status,
            policy_year=parsed.policy_year,
            parse_confidence=parsed.parse_confidence,
            parsing_session_id=session_uuid,
            structured_data=parsed.structured_data,
            plain_english_summary=parsed.plain_english_summary,
        )
        db.add(policy)
        await db.flush()  # Get policy.id

        # Create Benefits
        for benefit_data in parsed.benefits:
            benefit = Benefit(
                policy_id=policy.id,
                benefit_type=benefit_data.get("benefit_type", "other"),
                benefit_subtype=benefit_data.get("benefit_subtype"),
                trigger_description=benefit_data.get("trigger_description"),
                payout_type=benefit_data.get("payout_type"),
                amount_cents=benefit_data.get("amount_cents"),
                percentage_of_sum_assured=benefit_data.get("percentage_of_sum_assured"),
                survival_period_days=benefit_data.get("survival_period_days"),
                conditions=benefit_data.get("conditions"),
                exclusions=benefit_data.get("exclusions"),
                is_active=benefit_data.get("is_active", True),
                parse_confidence=benefit_data.get("parse_confidence", parsed.parse_confidence),
                raw_text_excerpt=benefit_data.get("raw_text_excerpt"),
            )
            db.add(benefit)

        await db.flush()

        # Create Riders (link to benefit if possible)
        for rider_data in parsed.riders:
            # Try to link to first matching benefit by type
            linked_benefit_id: uuid.UUID | None = None
            linked_type = rider_data.get("linked_benefit_type")
            if linked_type:
                benefit_result = await db.execute(
                    select(Benefit)
                    .where(Benefit.policy_id == policy.id)
                    .where(Benefit.benefit_type == linked_type)
                    .limit(1)
                )
                linked_benefit: Benefit | None = benefit_result.scalar_one_or_none()
                if linked_benefit:
                    linked_benefit_id = linked_benefit.id

            rider = Rider(
                policy_id=policy.id,
                rider_name=rider_data.get("rider_name", "Unknown Rider"),
                rider_type=rider_data.get("rider_type"),
                linked_benefit_id=linked_benefit_id,
                additional_premium_cents=rider_data.get("additional_premium_cents"),
                additional_sum_assured_cents=rider_data.get("additional_sum_assured_cents"),
                conditions=rider_data.get("conditions"),
                parse_confidence=rider_data.get("parse_confidence", parsed.parse_confidence),
            )
            db.add(rider)

        await db.flush()

        # Create Exclusions from structured_data if present
        exclusions_data = parsed.structured_data.get("exclusions", [])
        for exclusion_data in exclusions_data:
            if isinstance(exclusion_data, str):
                exclusion_text = exclusion_data
                exclusion_category = None
            else:
                exclusion_text = exclusion_data.get("exclusion_text", "")
                exclusion_category = exclusion_data.get("exclusion_category")

            exclusion = Exclusion(
                policy_id=policy.id,
                exclusion_text=exclusion_text,
                exclusion_category=exclusion_category,
                parse_confidence=parsed.parse_confidence,
            )
            db.add(exclusion)

        # Update ParsingSession status
        parsing_session.parse_status = "completed"
        parsing_session.completed_at = datetime.utcnow()
        if hasattr(parsed, "raw_json") and parsed.raw_json:
            raw = parsed.raw_json
            parsing_session.claude_model = raw.get("model_used", "claude-opus-4-5-20261120")
            # Estimate cost: $3/input-token + $15/output-token for Opus
            input_toks = raw.get("input_tokens", 0)
            output_toks = raw.get("output_tokens", 0)
            if input_toks or output_toks:
                parsing_session.tokens_used = input_toks + output_toks
                parsing_session.parse_cost_cents = int(
                    (input_toks * 3 + output_toks * 15) / 1_000_000 * 100
                )

        await db.commit()
        await db.refresh(policy)

        logger.info(
            f"Wrote Policy {policy.id} for user {user_id} "
            f"({len(parsed.benefits)} benefits, {len(parsed.riders)} riders)"
        )

        return policy
