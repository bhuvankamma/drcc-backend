"""
Pydantic schemas for employer login API (request/response).
"""
from pydantic import BaseModel, EmailStr, Field


class EmployerLoginRequest(BaseModel):
    """Request body for employer login."""

    email_address: EmailStr = Field(..., description="Employer email address")
    password: str = Field(..., min_length=1, description="Employer password")


class EmployerLoginResponse(BaseModel):
    """Success response after employer login."""

    message: str = Field(default="Login successful", description="Status message")
    employer_id: int = Field(..., description="Employer primary key")
    contact_person_name: str = Field(..., description="Contact person name")
    company_official_name: str = Field(..., description="Company official name")
    email_address: str = Field(..., description="Email address")

    class Config:
        from_attributes = True
