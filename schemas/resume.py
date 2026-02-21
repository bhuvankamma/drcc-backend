"""Resume & document schemas."""
from datetime import datetime

from pydantic import BaseModel


class ResumeOut(BaseModel):
    id: int
    filename: str
    upload_date: datetime
    file_type: str


class ResumeUploadResponse(BaseModel):
    id: int
    filename: str
    upload_date: datetime
    file_type: str


class ResumeUpdateIn(BaseModel):
    filename: str | None = None


class ResumeBuilderIn(BaseModel):
    """Resume builder form data (flexible)."""
    model_config = {"extra": "allow"}


class ResumeBuilderOut(BaseModel):
    """Resume builder stored data."""
    model_config = {"extra": "allow"}
