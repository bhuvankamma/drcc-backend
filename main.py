import os
from pathlib import Path

from fastapi import FastAPI, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from database.database import get_db
from models.user_profile import UserProfile
from routes.resume_docs import router as resume_router
<<<<<<< HEAD
from schemas.user_profile import ProfileUpdateSchema
#-------ram employer analytics ---------
from fastapi import FastAPI
from routes.employer_analytics_ram_router import router as analytics_router
#-------------------------------------------------------
#-----------ram admin dashboard--------
from fastapi import FastAPI
from routes.ram_admin_dashboard import router as dashboard_router


from routes.registrationUser import router as registration_router

app = FastAPI()
app.include_router(resume_router)
app.include_router(registration_router)
# Folder where uploaded files are saved (inside project)
UPLOAD_DIR = Path(__file__).resolve().parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

from fastapi import FastAPI
from routes.user_management import router as users_router
from database.database import get_connection


from fastapi.middleware.cors import CORSMiddleware

from database.database import engine, Base
from routes.admin_registration import router as admin_router





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
# admin dashboard user management
# ----------------------------------------

app.include_router(users_router, prefix="/users", tags=["Users"])

@app.on_event("startup")
def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS add_user (
            id SERIAL PRIMARY KEY,
            full_name VARCHAR(255) NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            role VARCHAR(50) NOT NULL DEFAULT 'User',
            status VARCHAR(20) NOT NULL DEFAULT 'Active',
            created_at TIMESTAMP NOT NULL DEFAULT NOW()
        );
    """)

    conn.commit()
    cursor.close()
    conn.close()


# ----------------------------------------
# admin registration
# ----------------------------------------
Base.metadata.create_all(bind=engine)

ALLOWED_ORIGINS = [
    "https://www.yuvasaathi.in",
    "http://localhost:3000",
    "https://www.yuvasaathiadmin.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(admin_router)

#---------------ram employer analytics----
# include analytics router
app.include_router(analytics_router)


@app.get("/")
def root():
    return {"message": "Analytics API running"}

#-----------ram admin dashboard------
# include dashboard router
app.include_router(dashboard_router)


@app.get("/")
def root():
    return {"message": "API running successfully"}
=======

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


