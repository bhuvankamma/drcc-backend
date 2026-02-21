"""Registration request schema."""
from typing import Optional
import re
from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator
from datetime import datetime


REGISTER_EXAMPLE = {
    "aadhaar_number": "123456789012",
    "certifications_skills": "AWS Certified Developer, Fluent in Python.",
    "confirm_password": "Test@1234",
    "country_code": "+91",
    "current_state": "Bihar",
    "email": "rahul.sharma@example.com",
    "employment_history": "3 years at ABC Corp as Web Developer. Key achievements: project X, Y.",
    "first_name": "Rahul",
    "highest_qualification": "Graduate",
    "middle_name": "Kumar",
    "mobile_number": "9876543210",
    "pan_number": "ADPWK0074K",
    "password": "Test@1234",
    "preferred_job_role": "Software Developer",
    "preferred_sector": "IT / Software",
    "previously_registered_exchange": False,
    "surname": "Sharma",
}


class ApplicantRegister(BaseModel):
    model_config = {"json_schema_extra": {"examples": [REGISTER_EXAMPLE]}}

    first_name: str = Field(..., min_length=1, max_length=100)
    middle_name: Optional[str] = Field(None, max_length=100)
    surname: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    country_code: str = Field(default="+91", max_length=5)
    mobile_number: str = Field(..., min_length=10, max_length=10)
    password: str = Field(..., min_length=8, max_length=72, description="8+ chars: upper, lower, number, special.")
    confirm_password: str = Field(..., min_length=8, max_length=72)
    aadhaar_number: Optional[str] = Field(None, max_length=12)
    pan_number: Optional[str] = Field(None, max_length=10)
    highest_qualification: str = Field(..., min_length=1)
    current_state: str = Field(..., min_length=1)
    preferred_sector: str = Field(..., min_length=1)
    preferred_job_role: str = Field(..., min_length=1)
    employment_history: Optional[str] = None
    certifications_skills: Optional[str] = None
    previously_registered_exchange: bool = False

    @field_validator("mobile_number")
    @classmethod
    def mobile_digits_only(cls, v: str) -> str:
        if not v.isdigit():
            raise ValueError("Mobile number must contain only digits")
        return v

    @model_validator(mode="after")
    def passwords_match(self):
        if self.password != self.confirm_password:
            raise ValueError("Password and confirm password do not match")
        return self

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>_\-+=\[\]\\;/'`~]", v):
            raise ValueError("Password must contain at least one special character")
        return v

    @field_validator("aadhaar_number")
    @classmethod
    def aadhaar_digits(cls, v: Optional[str]) -> Optional[str]:
        if v is None or v == "":
            return None
        if not v.isdigit() or len(v) != 12:
            raise ValueError("Aadhaar must be 12 digits")
        return v

    @field_validator("pan_number")
    @classmethod
    def pan_format(cls, v: Optional[str]) -> Optional[str]:
        if v is None or v == "":
            return None
        if not re.match(r"^[A-Z]{5}\d{4}[A-Z]$", v.upper()):
            raise ValueError("Invalid PAN format (e.g. ADPWK0074K)")
        return v.upper()





USER_RESPONSE_EXAMPLE = {
    "user_id": 1,
    "email": "rahul.sharma@example.com",
    "name": "Rahul Kumar Sharma",
    "role": "Employee",
    "phone_number": "+919876543210",
    "company_name": None,
    "department": "IT / Software - Software Developer",
    "address": "Bihar",
    "previous_ctc": None,
    "expected_ctc": None,
    "notice_period": None,
    "field_of_work": "IT / Software - Software Developer",
    "education": "Graduate",
    "experience": "3 years at ABC Corp as Web Developer. Key achievements: project X, Y.",
    "skills": "AWS Certified Developer, Fluent in Python.",
    "created_at": "2026-02-21T09:06:06.285Z",
}


class UserResponse(BaseModel):
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {"examples": [USER_RESPONSE_EXAMPLE]},
    }

    user_id: int
    email: str
    name: str
    role: str
    phone_number: Optional[str] = None
    company_name: Optional[str] = None
    department: Optional[str] = None
    address: Optional[str] = None
    previous_ctc: Optional[str] = None
    expected_ctc: Optional[str] = None
    notice_period: Optional[str] = None
    field_of_work: Optional[str] = None
    education: Optional[str] = None
    experience: Optional[str] = None
    skills: Optional[str] = None
    created_at: Optional[datetime] = None


class LookupItem(BaseModel):
    id: str
    label: str