from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ProfileResponse(BaseModel):
    id: int
    full_name: Optional[str] = None
    department: Optional[str] = None
    designation: Optional[str] = None
    govt_id: Optional[str] = None
    mobile_number: Optional[str] = None
    official_email: Optional[str] = None
    profile_picture_url: Optional[str] = None
    created_at: Optional[datetime] = None
    status: Optional[str] = None

    class Config:
        from_attributes = True


class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    department: Optional[str] = None
    designation: Optional[str] = None
    govt_id: Optional[str] = None
    mobile_number: Optional[str] = None
    official_email: Optional[str] = None


class PasswordChange(BaseModel):
    current_password: str
    new_password: str


class MessageResponse(BaseModel):
    message: str


class PictureResponse(BaseModel):
    profile_picture_url: str
