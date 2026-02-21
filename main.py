import os
from pathlib import Path

from fastapi import FastAPI, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from database.database import get_db

from routes.resume_docs import router as resume_router
from routes.registrationUser import router as registration_router
from routes.EmployerLogin import router as EmployerLogin_router
from routes.UserLogin import router as UserLogin_router

app = FastAPI()
app.include_router(EmployerLogin_router)
app.include_router(resume_router)
app.include_router(registration_router)
app.include_router(UserLogin_router)
# Folder where uploaded files are saved (inside project)
UPLOAD_DIR = Path(__file__).resolve().parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)













