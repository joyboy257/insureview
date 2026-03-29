export type ProductType =
  | "TERM_LIFE"
  | "WHOLE_LIFE"
  | "CRITICAL_ILLNESS"
  | "HOSPITALISATION"
  | "MEDISHIELD_LIFE"
  | "IP"
  | "DISABILITY"
  | "ACCIDENT"
  | "ENDOWMENT";

export type BenefitType =
  | "death"
  | "tpd"
  | "ci"
  | "hospitalisation"
  | "accident"
  | "disability"
  | "income";

export type PayoutType = "lumpsum" | "income_replacement" | "reimbursement";

export type RiderType =
  | "ci_rider"
  | "waiver"
  | "accelerated"
  | "supplementary";

export type PolicyStatus =
  | "active"
  | "lapsed"
  | "surrendered"
  | "reduced";

export type ParseStatus =
  | "pending"
  | "processing"
  | "completed"
  | "failed"
  | "review";

export interface Policy {
  id: string;
  insurerCode: string;
  insurerName: string;
  productName: string;
  productType: ProductType;
  policyNumber?: string;
  issueDate?: string;
  expiryDate?: string;
  sumAssuredCents: number;
  premiumAmountCents: number;
  premiumFrequency: "annual" | "monthly" | "quarterly";
  currency: string;
  policyStatus: PolicyStatus;
  policyYear?: number;
  parseConfidence: number;
  plainEnglishSummary?: string;
  structuredData?: PolicyStructuredData;
  createdAt: string;
  updatedAt: string;
}

export interface PolicyStructuredData {
  benefits: Benefit[];
  riders: Rider[];
  exclusions: Exclusion[];
}

export interface Benefit {
  id: string;
  policyId: string;
  benefitType: BenefitType;
  benefitSubtype?: string;
  triggerDescription: string;
  payoutType: PayoutType;
  amountCents?: number;
  percentageOfSumAssured?: number;
  survivalPeriodDays?: number;
  conditions?: Record<string, unknown>;
  exclusions?: Exclusion[];
  isActive: boolean;
  parseConfidence: number;
  rawTextExcerpt?: string;
  createdAt: string;
}

export interface Rider {
  id: string;
  policyId: string;
  riderName: string;
  riderType?: RiderType;
  linkedBenefitId?: string;
  additionalPremiumCents?: number;
  additionalSumAssuredCents?: number;
  conditions?: Record<string, unknown>;
  parseConfidence?: number;
  createdAt: string;
}

export interface Exclusion {
  id: string;
  policyId: string;
  benefitIds?: string[];
  exclusionText: string;
  exclusionCategory?: string;
  parseConfidence?: number;
  createdAt: string;
}
