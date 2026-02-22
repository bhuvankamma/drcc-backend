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

from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from database.database import engine, Base
import models  # noqa: F401 - register models with Base
from routes.admin_profile import router as admin_profile

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

# ----------------------------------------
# admin profile
# ----------------------------------------


app = FastAPI(title="Admin Profile API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
UPLOAD_URL_PREFIX = os.getenv("UPLOAD_URL_PREFIX", "/uploads/")
Path(UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
app.mount(UPLOAD_URL_PREFIX.rstrip("/"), StaticFiles(directory=UPLOAD_DIR), name="uploads")

app.include_router(admin_profile)


@app.get("/")
def root():
    static_file = Path(__file__).parent / "static" / "index.html"
    if static_file.exists():
        return FileResponse(static_file)
    return {"message": "Admin Profile API", "docs": "/docs"}


static_path = Path(__file__).parent / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")
