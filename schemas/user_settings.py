from datetime import datetime
from pydantic import BaseModel, EmailStr
from typing import Optional


class UserBase(BaseModel):
    email: EmailStr
    name: str
    role: Optional[str] = None
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
    profile_picture: Optional[str] = None  # URL or path for profile image


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    role: Optional[str] = None
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
    profile_picture: Optional[str] = None


class ProfilePictureUpdate(BaseModel):
    profile_picture: Optional[str] = None  # URL or path; empty string to clear


class PasswordChange(BaseModel):
    current_password: str
    new_password: str
