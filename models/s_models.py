from pydantic import BaseModel, HttpUrl
from typing import Optional


# =========================
# CREATE JOB MODEL
# =========================
class JobCreate(BaseModel):
    reference_id: Optional[str] = None

    title: str
    description: str
    company_name: str

    location: Optional[str] = None
    experience: Optional[str] = None
    industry: Optional[str] = None

    min_salary: Optional[float] = None
    max_salary: Optional[float] = None

    application_url: Optional[HttpUrl] = None


# =========================
# UPDATE JOB MODEL
# =========================
class JobUpdate(BaseModel):
    reference_id: Optional[str] = None

    title: Optional[str] = None
    description: Optional[str] = None
    company_name: Optional[str] = None

    location: Optional[str] = None
    experience: Optional[str] = None
    industry: Optional[str] = None

    min_salary: Optional[float] = None
    max_salary: Optional[float] = None

    application_url: Optional[HttpUrl] = None
    status: Optional[str] = None