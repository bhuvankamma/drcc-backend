# app/schemas/admin.py

from typing import Optional
from pydantic import BaseModel, EmailStr

class AdminActionRequest(BaseModel):
    action: str
    full_name: Optional[str] = None
    department: Optional[str] = None
    designation: Optional[str] = None
    govt_id: Optional[str] = None
    mobile_number: Optional[str] = None
    official_email: Optional[EmailStr] = None
    password: Optional[str] = None
    confirm_password: Optional[str] = None