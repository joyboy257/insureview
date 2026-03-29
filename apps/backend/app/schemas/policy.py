from datetime import datetime, date
from uuid import UUID
from pydantic import BaseModel, Field


class BenefitSchema(BaseModel):
    id: UUID
    benefit_type: str
    benefit_subtype: str | None = None
    trigger_description: str | None = None
    payout_type: str | None = None
    amount_cents: int | None = None
    percentage_of_sum_assured: float | None = None
    survival_period_days: int | None = None
    conditions: dict | None = None
    exclusions: list[dict] | None = None
    is_active: bool = True
    parse_confidence: float = 0.0
    raw_text_excerpt: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class RiderSchema(BaseModel):
    id: UUID
    rider_name: str
    rider_type: str | None = None
    linked_benefit_id: UUID | None = None
    additional_premium_cents: int | None = None
    additional_sum_assured_cents: int | None = None
    conditions: dict | None = None
    parse_confidence: float | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ExclusionSchema(BaseModel):
    id: UUID
    exclusion_text: str
    exclusion_category: str | None = None
    parse_confidence: float | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class PolicyBase(BaseModel):
    insurer_code: str
    insurer_name: str
    product_name: str
    product_type: str
    policy_number: str | None = None
    issue_date: date | None = None
    expiry_date: date | None = None
    sum_assured_cents: int = 0
    premium_amount_cents: int | None = None
    premium_frequency: str = "annual"
    currency: str = "SGD"
    policy_status: str = "active"


class PolicySummary(PolicyBase):
    id: UUID
    parse_confidence: float
    plain_english_summary: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PolicyDetail(PolicySummary):
    benefits: list[BenefitSchema] = []
    riders: list[RiderSchema] = []
    exclusions: list[ExclusionSchema] = []

    model_config = {"from_attributes": True}
