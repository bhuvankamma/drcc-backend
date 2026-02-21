"""
Pydantic schemas for auth request/response.
"""
from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """Email/Mobile and password for generating OTP."""
    email: str = Field(..., description="Registered email or 10-digit mobile")
    password: str = Field(..., min_length=1, description="Password")


class GenerateOTPResponse(BaseModel):
    """Response after OTP is sent."""
    message: str = "OTP sent to your registered email. Valid for 5 minutes."
    email: str


class VerifyOTPRequest(BaseModel):
    """Email and OTP for verification."""
    email: str = Field(..., description="Registered email")
    otp: str = Field(..., min_length=6, max_length=6, description="6-digit OTP")


class TokenResponse(BaseModel):
    """JWT token and user info after successful OTP verification."""
    access_token: str
    token_type: str = "bearer"
    user_id: int
    email: str
    name: str
    role: str | None = None


class UserProfileResponse(BaseModel):
    """Minimal user info (for token response)."""
    user_id: int
    email: str
    name: str
    role: str | None = None

    class Config:
        from_attributes = True
