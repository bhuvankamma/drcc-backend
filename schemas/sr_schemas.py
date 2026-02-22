# app/schemas.py

from pydantic import BaseModel, EmailStr


class RecruiterInvite(BaseModel):
    name: str
    email: EmailStr
    role: str
    company_name: str