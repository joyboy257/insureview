from datetime import datetime
from uuid import UUID
from pydantic import BaseModel


class AnalysisRequest(BaseModel):
    policy_ids: list[UUID] | None = None


class OverlappingPolicySchema(BaseModel):
    policy_id: str
    product_name: str
    insurer: str
    sum_assured_cents: int


class CoverageGapSchema(BaseModel):
    coverage_type: str
    severity: str
    description: str
    recommendation: str | None = None
    current_amount_cents: int | None = None
    gap_amount_cents: int | None = None
    covered_by_policy_ids: list[str] = []
    benchmark_amount: str | None = None
    benchmark_source: str | None = None
    user_specific_note: str | None = None
    confidence: float


class PolicyOverlapSchema(BaseModel):
    coverage_type: str
    severity: str
    overlapping_policies: list[OverlappingPolicySchema]
    policy_count: int
    total_sum_assured_cents: int
    note: str
    overlap_type: str | None = None
    policies_involved: list[str] = []
    benefit_ids: list[str] = []
    interaction_description: str | None = None
    payout_order_note: str | None = None
    waste_estimate_cents: int | None = None
    conflict_flag: bool = False


class AffectedPolicySchema(BaseModel):
    policy_id: str
    product_name: str
    insurer: str
    detail: dict | None = None


class PolicyConflictSchema(BaseModel):
    conflict_type: str
    severity: str
    description: str
    affected_policies: list[AffectedPolicySchema]
    resolution_hint: str
    conflict_id: str | None = None
    policies_involved: list[str] = []
    benefit_ids: list[str] = []
    policy_a_term: str | None = None
    policy_b_term: str | None = None
    plain_english_explanation: str | None = None
    action_required: str | None = None


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
