import os
from pathlib import Path
from fastapi import FastAPI, Depends, File, HTTPException, UploadFile
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Database imports
from database.database import get_db, engine, Base, get_connection
import models.user_settings  # Ensures models are registered
import models.system_settings 
from models.user_profile import UserProfile
from schemas.user_profile import ProfileUpdateSchema

# Router imports
from routes.resume_docs import router as resume_router
from routes.registrationUser import router as registration_router
from routes.EmployerLogin import router as EmployerLogin_router
from routes.UserLogin import router as UserLogin_router
from routes.EmployerRegistration import router as registrationemployer_router
from routes.employer_analytics_ram_router import router as analytics_router
from routes.ram_admin_dashboard import router as dashboard_router
from routes.user_management import router as users_router
from routes.admin_registration import router as admin_router
from routes.admin_login import router as auth_router
from routes.user_settings import router as user_settings_router
from routes.system_settings import router as system_settings_router

app = FastAPI(title="DRCC Backend API")

# Setup Directories
UPLOAD_DIR = Path(__file__).resolve().parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

# CORS Configuration
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

# --- Include All Routers ---
app.include_router(auth_router, tags=["Admin Auth"])
app.include_router(UserLogin_router, tags=["User Login"])
app.include_router(EmployerLogin_router, tags=["Employer Login"])
app.include_router(registrationemployer_router, tags=["Employer Registration"])
app.include_router(resume_router, tags=["Resumes"])
app.include_router(registration_router, tags=["Registration"])
app.include_router(users_router, prefix="/users", tags=["Users"])
app.include_router(admin_router, tags=["Admin Registration"])
app.include_router(analytics_router, tags=["Analytics"])
app.include_router(dashboard_router, tags=["Dashboard"])
app.include_router(user_settings_router, tags=["User Settings"])
app.include_router(system_settings_router, tags=["System Settings"])

# --- Endpoints ---

@app.get("/", tags=["Root"])
def root():
    # Automatically redirect users to /docs for easier testing
    return RedirectResponse(url="/docs", status_code=302)

@app.put("/user/{user_id}", tags=["Profile"])
def update_user_profile(user_id: int, data: ProfileUpdateSchema, db: Session = Depends(get_db)):
    # Note: This specific endpoint will throw an error if called because it uses the DB session
    user = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    for key, value in data.dict().items():
        if value is not None:
            setattr(user, key, value)
    
    db.commit()
    db.refresh(user)
    return {"message": "Profile updated successfully", "user_id": user.user_id}

@app.post("/upload", tags=["Upload"])
async def upload_files(files: list[UploadFile] = File(...)):
    saved = []
    for f in files:
        if not f.filename: continue
        safe_name = os.path.basename(f.filename).strip()
        dest = UPLOAD_DIR / safe_name
        content = await f.read()
        dest.write_bytes(content)
        saved.append({"filename": safe_name, "path": str(dest)})
    return {"message": "Files saved", "files": saved}

@app.on_event("startup")
def startup_db_setup():
    # COMPLETELY BYPASSED DATABASE LOGIC
    # We are skipping Base.metadata.create_all and raw SQL checks
    print("--------------------------------------------------")
    print("DATABASE BYPASS: All API routes loaded successfully.")
    print("You can now view all merged modules at /docs")
    print("--------------------------------------------------")
    pass

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)