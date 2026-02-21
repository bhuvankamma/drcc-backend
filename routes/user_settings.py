import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse, HTMLResponse
from sqlalchemy.orm import Session

import crud
from schemas.user_settings import UserRead, UserUpdate, ProfilePictureUpdate, PasswordChange
from database.database import get_db

router = APIRouter()

UPLOAD_DIR = Path(__file__).resolve().parent / "uploads"
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}


# -----------------------------
# Profile Page
# -----------------------------

@router.get("/profile", response_class=HTMLResponse)
def profile_page():
    path = Path(__file__).resolve().parent / "static" / "profile.html"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Profile page not found")
    return FileResponse(path)


# -----------------------------
# Get User
# -----------------------------

@router.get("/user/{user_id}", response_model=UserRead)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# -----------------------------
# Update User
# -----------------------------

@router.put("/user/{user_id}", response_model=UserRead)
def update_user(user_id: int, user: UserUpdate, db: Session = Depends(get_db)):
    updated = crud.update_user(db, user_id, user)
    if not updated:
        raise HTTPException(status_code=404, detail="User not found")
    return updated


# -----------------------------
# Update Profile Picture (URL)
# -----------------------------

@router.put("/user/{user_id}/profile-picture", response_model=UserRead)
def update_profile_picture(user_id: int, data: ProfilePictureUpdate, db: Session = Depends(get_db)):
    updated = crud.update_user(db, user_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="User not found")
    return updated


# -----------------------------
# Upload Profile Picture (File)
# -----------------------------

@router.post("/user/{user_id}/profile-picture/upload", response_model=UserRead)
async def upload_profile_picture(
    user_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Only image files are allowed (JPEG, PNG, GIF, WebP)",
        )

    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    ext = Path(file.filename or "image").suffix.lower() or ".jpg"
    if ext not in (".jpg", ".jpeg", ".png", ".gif", ".webp"):
        ext = ".jpg"

    safe_name = f"user_{user_id}_{uuid.uuid4().hex[:12]}{ext}"
    path = UPLOAD_DIR / safe_name

    content = await file.read()
    path.write_bytes(content)

    url_path = f"/uploads/{safe_name}"

    updated = crud.update_user(
        db,
        user_id,
        ProfilePictureUpdate(profile_picture=url_path),
    )

    return updated


# -----------------------------
# Change Password
# -----------------------------

@router.put("/user/{user_id}/change-password")
def change_password(user_id: int, password_data: PasswordChange, db: Session = Depends(get_db)):
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not crud.pwd_context.verify(password_data.current_password, user.password):
        raise HTTPException(status_code=400, detail="Current password is incorrect")

    crud.change_password(db, user_id, password_data.new_password)

    return {"detail": "Password updated successfully"}


# -----------------------------
# Delete User
# -----------------------------

@router.delete("/user/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    crud.delete_user(db, user_id)

    return {"detail": "User deleted successfully"}