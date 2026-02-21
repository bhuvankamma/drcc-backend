from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from database.database import Base, engine
import models.user_settings  # IMPORTANT: ensures models are registered
from routes.user_settings import router as user_router

app = FastAPI()
import os
from pathlib import Path
from database.database import Base, engine, get_db
from routes.admin_login import router as auth_router
import models.system_settings
from routes.system_settings import router as system_settings_router

# ----------------------------------------
# admin login
# ----------------------------------------


app.include_router(auth_router)
# ----------------------------------------
# system_settings
# ----------------------------------------
# run in .venv environment
app.include_router(system_settings_router)


# ----------------------------------------
# user_settings
# ----------------------------------------

# Uploads directory
UPLOAD_DIR = Path(__file__).resolve().parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

# Include router
app.include_router(user_router)

@app.get("/")
def root():
    return RedirectResponse(url="/docs", status_code=302)