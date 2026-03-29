import axios from "axios";

const API_BASE =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

// snake_case → camelCase converter for API responses
function snakeToCamel(obj: unknown): unknown {
  if (Array.isArray(obj)) return obj.map(snakeToCamel);
  if (obj !== null && typeof obj === "object") {
    return Object.fromEntries(
      Object.entries(obj as Record<string, unknown>).map(([k, v]) => [
        k.replace(/_([a-z])/g, (_, c) => c.toUpperCase()),
        snakeToCamel(v),
      ])
    );
  }
  return obj;
}

export const api = axios.create({
  baseURL: API_BASE,
  headers: { "Content-Type": "application/json" },
});

api.interceptors.response.use((response) => {
  if (response.data) {
    response.data = snakeToCamel(response.data);
  }
  return response;
});

api.interceptors.request.use((config) => {
  const token = typeof window !== "undefined" ? localStorage.getItem("session_token") : null;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export interface PolicySummary {
  id: string;
  insurerCode: string;
  insurerName: string;
  productName: string;
  productType: string;
  policyNumber: string | null;
  issueDate: string | null;
  expiryDate: string | null;
  sumAssuredCents: number;
  premiumAmountCents: number | null;
  premiumFrequency: string;
  currency: string;
  policyStatus: string;
  policyYear: number | null;
  parseConfidence: number;
  structuredData: Record<string, unknown>;
  plainEnglishSummary: string | null;
  createdAt: string;
}

export interface Benefit {
  id: string;
  policyId: string;
  benefitType: string;
  benefitSubtype: string | null;
  triggerDescription: string | null;
  payoutType: string | null;
  amountCents: number | null;
  percentageOfSumAssured: number | null;
  survivalPeriodDays: number | null;
  conditions: Record<string, unknown> | null;
  exclusions: Record<string, unknown> | null;
  isActive: boolean;
  parseConfidence: number;
  rawTextExcerpt: string | null;
}

export interface Rider {
  id: string;
  policyId: string;
  riderName: string;
  riderType: string | null;
  linkedBenefitId: string | null;
  additionalPremiumCents: number | null;
  additionalSumAssuredCents: number | null;
  conditions: Record<string, unknown> | null;
  parseConfidence: number | null;
}

export interface Exclusion {
  id: string;
  policyId: string;
  benefitIds: string[] | null;
  exclusionText: string;
  exclusionCategory: string | null;
  parseConfidence: number | null;
}

export interface PolicyDetail extends PolicySummary {
  benefits: Benefit[];
  riders: Rider[];
  exclusions: Exclusion[];
}

export interface UploadPresignedUrlRequest {
  filename: string;
  fileSizeBytes: number;
}

export interface UploadPresignedUrlResponse {
  uploadUrl: string;
  s3Key: string;
  expiresAt: string;
}

export interface ParsingSession {
  id: string;
  status: "pending" | "processing" | "completed" | "failed" | "review";
  originalFilename: string | null;
  documentType: string | null;
  parseError: string | null;
  completedAt: string | null;
}

export async function getPolicies(): Promise<PolicySummary[]> {
  const { data } = await api.get<PolicySummary[]>("/policies");
  return data;
}

export async function getPolicy(id: string): Promise<PolicyDetail> {
  const { data } = await api.get<PolicyDetail>(`/policies/${id}`);
  return data;
}

export async function getUploadPresignedUrl(
  req: UploadPresignedUrlRequest
): Promise<UploadPresignedUrlResponse> {
  const { data } = await api.post<UploadPresignedUrlResponse>(
    "/upload/presigned-url",
    req
  );
  return data;
}

export async function getParsingSession(id: string): Promise<ParsingSession> {
  const { data } = await api.get<ParsingSession>(`/parse/${id}`);
  return data;
}

export async function triggerAnalysis(
  policyIds?: string[]
): Promise<{ id: string }> {
  const { data } = await api.post<{ id: string }>("/analysis", {
    policy_ids: policyIds,
  });
  return data;
}

export async function completeUpload(sessionId: string): Promise<{ status: string }> {
  const { data } = await api.post<{ status: string }>(`/upload/complete-upload/${sessionId}`);
  return data;
}
