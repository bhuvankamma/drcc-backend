from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


# =====================================
# USER SCHEMAS
# =====================================

class UserBase(BaseModel):
    full_name: str
    email: EmailStr
    role: str
    status: str


class UserResponse(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True   # use this if Pydantic v2
        # orm_mode = True        # use this instead if Pydantic v1


class UserRoleUpdate(BaseModel):
    role: str


# =====================================
# ANNOUNCEMENT SCHEMAS
# =====================================

class AnnouncementCreate(BaseModel):
    message: str


class AnnouncementResponse(BaseModel):
    id: int
    message: str
    created_by: int
    created_at: datetime

    class Config:
        from_attributes = True


# =====================================
# NOTIFICATION SCHEMAS
# =====================================

class NotificationResponse(BaseModel):
    id: int
    user_id: int
    announcement_id: int
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True


class MarkNotificationRead(BaseModel):
    is_read: bool


# =====================================
# SYSTEM CONFIGURATION SCHEMAS
# =====================================

class ConfigUpdate(BaseModel):
    max_job_postings: int
    enable_user_registration: bool
    require_admin_approval: bool
    email_notifications: bool


class ConfigResponse(BaseModel):
    id: int
    max_job_postings: int
    enable_user_registration: bool
    require_admin_approval: bool
    email_notifications: bool
    updated_at: datetime

    class Config:
        from_attributes = True