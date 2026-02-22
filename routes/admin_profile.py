import os
import uuid
import shutil
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from passlib.exc import UnknownHashError

from database.database import get_db
from models.admin_profile import Admin
from schemas.admin_profile import ProfileResponse, ProfileUpdate, PasswordChange, MessageResponse, PictureResponse

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
UPLOAD_URL_PREFIX = os.getenv("UPLOAD_URL_PREFIX", "/uploads/")
Path(UPLOAD_DIR).mkdir(parents=True, exist_ok=True)

router = APIRouter(prefix="/api", tags=["profile"])


def get_admin_id(admin_id: int = Query(..., description="Current admin ID (use auth in production)")):
    return admin_id


def get_current_admin(
    admin_id: int = Depends(get_admin_id),
    db: Session = Depends(get_db),
) -> Admin:
    admin = db.query(Admin).filter(Admin.id == admin_id).first()
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")
    return admin


@router.get("/profile", response_model=ProfileResponse)
def get_profile(admin: Admin = Depends(get_current_admin)):
    return admin


@router.put("/profile", response_model=MessageResponse)
def update_profile(
    body: ProfileUpdate,
    admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    data = body.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(admin, k, v)
    db.commit()
    db.refresh(admin)
    return MessageResponse(message="Profile updated")


@router.post("/profile/picture", response_model=PictureResponse)
def change_profile_picture(
    file: UploadFile = File(...),
    admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files allowed")
    ext = Path(file.filename or "img").suffix or ".png"
    name = f"admin_{admin.id}_{uuid.uuid4().hex}{ext}"
    path = Path(UPLOAD_DIR) / name
    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    url = f"{UPLOAD_URL_PREFIX}{name}"
    admin.profile_picture_url = url
    db.commit()
    return PictureResponse(profile_picture_url=url)


def _verify_current_password(plain_password: str, stored_password: str) -> bool:
    """Verify current password. Supports bcrypt hashes or legacy plain-text storage."""
    if not stored_password:
        return False
    try:
        return pwd_ctx.verify(plain_password, stored_password)
    except UnknownHashError:
        # Legacy: password may be stored in plain text
        return plain_password == stored_password


@router.post("/profile/change-password", response_model=MessageResponse)
def change_password(
    body: PasswordChange,
    admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    if not _verify_current_password(body.current_password, admin.password):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    admin.password = pwd_ctx.hash(body.new_password)
    db.commit()
    return MessageResponse(message="Password updated")
