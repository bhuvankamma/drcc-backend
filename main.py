from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from database.database import get_db
from models.user_profile import UserProfile
from schemas.user_profile import ProfileUpdateSchema
#-------ram employer analytics ---------
from fastapi import FastAPI
from routes.employer_analytics_ram_router import router as analytics_router
#-------------------------------------------------------
#-----------ram admin dashboard--------
from fastapi import FastAPI
from routes.ram_admin_dashboard import router as dashboard_router

app = FastAPI()

from fastapi import FastAPI
from routes.user_management import router as users_router
from database.database import get_connection


from fastapi.middleware.cors import CORSMiddleware

from database.database import engine, Base
from routes.admin_registration import router as admin_router

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