from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field


class PresignedUrlRequest(BaseModel):
    filename: str = Field(..., max_length=500)
    file_size_bytes: int = Field(..., gt=0, le=52_428_800)  # 50MB max


class PresignedUrlResponse(BaseModel):
    upload_url: str
    s3_key: str
    expires_at: datetime


class ConsentRequest(BaseModel):
    consent_type: str = Field(..., pattern="^(pdpa_upload|pdpa_analysis|vault_optin|claims_submission)$")
    consent_version: str


class ConsentRecordResponse(BaseModel):
    id: UUID
    consent_type: str
    consent_version: str
    given_at: datetime

    model_config = {"from_attributes": True}
