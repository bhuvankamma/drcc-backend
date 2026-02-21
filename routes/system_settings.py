from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.database import get_db
from models.system_settings import User, Announcement, Notification, SystemConfiguration
from typing import List

from schemas.system_settings import (
    UserResponse,
    UserRoleUpdate,
    AnnouncementCreate,
    ConfigUpdate
)

router = APIRouter()
# =====================================
# USERS - Manage Roles
# =====================================

@router.get("/users", response_model=list[UserResponse])
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()


@router.put("/users/{user_id}/role")
def update_user_role(user_id: int, data: UserRoleUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.role = data.role
    db.commit()
    db.refresh(user)

    return {"message": "Role updated successfully"}


# =====================================
# SEND ANNOUNCEMENT
# =====================================

@router.post("/announcements")
def send_announcement(data: AnnouncementCreate, db: Session = Depends(get_db)):

    # 1️⃣ Create announcement
    announcement = Announcement(
        message=data.message,
    )
    db.add(announcement)
    db.commit()
    db.refresh(announcement)

    # 2️⃣ Get active users & employers
    recipients = db.query(User).filter(
        User.role.in_(["user", "employer"]),
        User.status == "Active"
    ).all()

    # 3️⃣ Create notifications
    for user in recipients:
        notification = Notification(
            user_id=user.id,
            announcement_id=announcement.id
        )
        db.add(notification)

    db.commit()

    return {"message": "Announcement sent successfully"}


# =====================================
# SYSTEM CONFIGURATION
# =====================================

@router.get("/config")
def get_config(db: Session = Depends(get_db)):
    config = db.query(SystemConfiguration).first()

    if not config:
        config = SystemConfiguration()
        db.add(config)
        db.commit()
        db.refresh(config)

    return config


@router.put("/config")
def update_config(data: ConfigUpdate, db: Session = Depends(get_db)):
    config = db.query(SystemConfiguration).first()

    if not config:
        raise HTTPException(status_code=404, detail="Configuration not found")

    config.max_job_postings = data.max_job_postings
    config.enable_user_registration = data.enable_user_registration
    config.require_admin_approval = data.require_admin_approval
    config.email_notifications = data.email_notifications

    db.commit()

    return {"message": "Configuration updated successfully"}