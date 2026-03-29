import uuid
from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr, Field


class SandboxApplication(BaseModel):
    company_name: str = Field(..., min_length=1, max_length=255)
    contact_email: EmailStr
    website: str = Field(default="")
    product_description: str = Field(..., min_length=1)
    target_users: str = Field(..., min_length=1)
    proposed_timeline: Literal["6_months", "12_months"]
    expected_users: int = Field(default=0, ge=0)


class SandboxResponse(BaseModel):
    status: str
    application_id: str
    next_steps: str


router = APIRouter()


@router.post("/sandbox", response_model=SandboxResponse)
async def submit_sandbox_application(application: SandboxApplication) -> SandboxResponse:
    """
    Submit a MAS FinTech Sandbox application.
    This endpoint is public — no authentication required.
    """
    application_id = str(uuid.uuid4())

    print(f"[Sandbox Application Received]")
    print(f"  Application ID : {application_id}")
    print(f"  Company         : {application.company_name}")
    print(f"  Contact Email   : {application.contact_email}")
    print(f"  Website         : {application.website}")
    print(f"  Timeline        : {application.proposed_timeline}")
    print(f"  Expected Users  : {application.expected_users}")
    print(f"  Product Desc    : {application.product_description[:120]}...")
    print(f"  Target Users    : {application.target_users}")
    print(f"---")

    return SandboxResponse(
        status="received",
        application_id=application_id,
        next_steps="MAS will review and respond within 5 business days",
    )
