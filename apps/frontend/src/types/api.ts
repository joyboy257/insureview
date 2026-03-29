export interface ApiResponse<T> {
  data: T;
  masDisclaimer: string;
  generatedAt: string;
  disclaimerVersion: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
}

export interface ApiError {
  detail: string;
  code?: string;
}

export interface PresignedUploadRequest {
  filename: string;
  fileSizeBytes: number;
  contentType: string;
}

export interface PresignedUploadResponse {
  uploadUrl: string;
  s3Key: string;
  expiresAt: string;
}

export interface ConsentRequest {
  consentType: "pdpa_upload" | "pdpa_analysis" | "vault_optin";
  consentVersion: string;
}

export interface ConsentResponse {
  id: string;
  givenAt: string;
}
