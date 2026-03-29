export type CoverageType =
  | "DEATH"
  | "TPD"
  | "CI"
  | "HOSPITALISATION"
  | "MEDISHIELD_LIFE"
  | "IP"
  | "ACCIDENT"
  | "DISABILITY";

export type GapSeverity = "missing" | "partial" | "adequate";

export interface CoverageGap {
  coverageType: CoverageType;
  severity: GapSeverity;
  description: string;
  currentAmountCents?: number;
  benchmarkAmount?: string;
  benchmarkSource?: string;
  userSpecificNote?: string;
  confidence: number;
}

export interface PolicyOverlap {
  overlapType: string;
  policiesInvolved: string[];
  benefitIds: string[];
  coverageType: CoverageType;
  totalOverlappingAmountCents: number;
  interactionDescription: string;
  payoutOrderNote?: string;
  wasteEstimateCents?: number;
  conflictFlag: boolean;
}

export interface PolicyConflict {
  conflictId: string;
  conflictType: "trigger_mismatch" | "exclusion_contradiction" | "payout_cap_conflict" | "definition_conflict";
  policiesInvolved: string[];
  benefitIds: string[];
  severity: "critical" | "moderate" | "minor";
  conflictDescription: string;
  policyATerm: string;
  policyBTerm: string;
  resolutionNote: string;
  plainEnglishExplanation: string;
  actionRequired: "review_with_insurer" | "no_action" | "consult_advisor";
}

export interface ScenarioResult {
  scenarioId: string;
  scenarioLabel: string;
  events: string[];
  policiesThatPay: Array<{
    policyId: string;
    amountCents: number;
    benefitType: string;
  }>;
  totalPayoutCents: number;
  payoutTimeline: Array<{
    month: number;
    amountCents: number;
    source: string;
  }>;
  incomeReplacementMonths?: number;
  plainEnglishNarrative: string;
  masCompliant: boolean;
}

export interface PortfolioAnalysis {
  gaps: CoverageGap[];
  overlaps: PolicyOverlap[];
  conflicts: PolicyConflict[];
  scenarios: ScenarioResult[];
  plainEnglishSummary: string;
}
