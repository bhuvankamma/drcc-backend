from pydantic import BaseModel
from typing import Optional, Dict


class TemplateResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    preview_url: Optional[str]

    class Config:
        from_attributes = True


class ResumeCreate(BaseModel):
    user_id: int
    template_id: int
    resume_data: Dict


class ResumeResponse(BaseModel):
    id: int
    user_id: int
    template_id: int
    resume_data: str

    class Config:
        from_attributes = True