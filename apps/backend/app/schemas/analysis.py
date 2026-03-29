from datetime import datetime
from uuid import UUID
from pydantic import BaseModel


class AnalysisRequest(BaseModel):
    policy_ids: list[UUID] | None = None


class CoverageGapSchema(BaseModel):
    coverage_type: str
    severity: str
    description: str
    current_amount_cents: int | None = None
    benchmark_amount: str | None = None
    benchmark_source: str | None = None
    user_specific_note: str | None = None
    confidence: float


class PolicyOverlapSchema(BaseModel):
    overlap_type: str
    policies_involved: list[str]
    benefit_ids: list[str]
    coverage_type: str
    total_overlapping_amount_cents: int
    interaction_description: str
    payout_order_note: str | None = None
    waste_estimate_cents: int | None = None
    conflict_flag: bool


class PolicyConflictSchema(BaseModel):
    conflict_id: str
    conflict_type: str
    policies_involved: list[str]
    benefit_ids: list[str]
    severity: str
    conflict_description: str
    policy_a_term: str
    policy_b_term: str
    resolution_note: str
    plain_english_explanation: str
    action_required: str


class ScenarioPayoutItem(BaseModel):
    policy_id: str
    amount_cents: int
    benefit_type: str


class ScenarioPayoutTimeline(BaseModel):
    month: int
    amount_cents: int
    source: str


class ScenarioResultSchema(BaseModel):
    scenario_id: str
    scenario_label: str
    events: list[str]
    policies_that_pay: list[ScenarioPayoutItem]
    total_payout_cents: int
    payout_timeline: list[ScenarioPayoutItem]
    income_replacement_months: int | None = None
    plain_english_narrative: str
    mas_compliant: bool = True


class AnalysisOutputSchema(BaseModel):
    gaps: list[CoverageGapSchema] = []
    overlaps: list[PolicyOverlapSchema] = []
    conflicts: list[PolicyConflictSchema] = []
    scenarios: list[ScenarioResultSchema] = []
    plain_english_summary: str


class AnalysisResponse(BaseModel):
    data: AnalysisOutputSchema
    mas_disclaimer: str
    generated_at: datetime
    disclaimer_version: str


class AnalysisResultSummary(BaseModel):
    id: UUID
    analysis_type: str
    trigger: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
