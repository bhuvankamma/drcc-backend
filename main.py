import os
from pathlib import Path

from fastapi import FastAPI, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from database.database import get_db
from models.user_profile import UserProfile
from routes.resume_docs import router as resume_router
from schemas.user_profile import ProfileUpdateSchema

app = FastAPI()
app.include_router(resume_router)

# Folder where uploaded files are saved (inside project)
UPLOAD_DIR = Path(__file__).resolve().parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)


# ----------------------------------------
# GET PROFILE (Dashboard Load)
# ----------------------------------------
@app.get("/profile/{user_id}")
def get_profile(user_id: int, db: Session = Depends(get_db)):

    user = db.query(UserProfile).filter(
        UserProfile.user_id == user_id
    ).first()

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return {
        "user_id": user.user_id,
        "email": user.email,
        "name": user.name,
        "role": user.role,
        "phone_number": user.phone_number,
        "company_name": user.company_name,
        "department": user.department,
        "address": user.address,
        "previous_ctc": user.previous_ctc,
        "expected_ctc": user.expected_ctc,
        "notice_period": user.notice_period,
        "field_of_work": user.field_of_work,
        "education": user.education,
        "experience": user.experience,
        "skills": user.skills
    }


# ----------------------------------------
# UPDATE PROFILE (Edit Profile Save)
# ----------------------------------------
@app.put("/profile/{user_id}")
def update_profile(
    user_id: int,
    data: ProfileUpdateSchema,
    db: Session = Depends(get_db)
):

    user = db.query(UserProfile).filter(
        UserProfile.user_id == user_id
    ).first()

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # Update only editable fields
    user.address = data.address
    user.previous_ctc = data.previous_ctc
    user.expected_ctc = data.expected_ctc
    user.notice_period = data.notice_period
    user.field_of_work = data.field_of_work
    user.education = data.education
    user.experience = data.experience
    user.skills = data.skills

    db.commit()
    db.refresh(user)

    return {
        "message": "Profile updated successfully",
        "user_id": user.user_id
    }


# ----------------------------------------
# FILE UPLOAD (save files into project folder)
# ----------------------------------------
@app.post("/upload")
async def upload_files(files: list[UploadFile] = File(...)):
    """Accept one or more file uploads and save them into the uploads folder."""
    saved = []
    for f in files:
        if not f.filename or f.filename.strip() == "":
            continue
        # Safe filename (avoid path traversal)
        safe_name = os.path.basename(f.filename).strip()
        if not safe_name:
            continue
        dest = UPLOAD_DIR / safe_name
        try:
            content = await f.read()
            dest.write_bytes(content)
            saved.append({"filename": safe_name, "path": str(dest)})
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to save {f.filename}: {e}")
    if not saved:
        raise HTTPException(status_code=400, detail="No valid files to upload.")
    return {"message": "Files saved to folder", "files": saved}
