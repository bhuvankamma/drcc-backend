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


from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
import pg8000

from database.s_db import get_connection
from models.s_models import JobCreate, JobUpdate

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.sr_config import settings
from routes.sr_routes import router

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


SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

security = HTTPBearer()

# ===============================
# TOKEN CREATION
# ===============================
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# ===============================
# AUTH DEPENDENCY
# ===============================
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        role = payload.get("role")

        if not user_id or not role:
            raise HTTPException(status_code=401, detail="Invalid token")

        return {"user_id": user_id, "role": role}

    except JWTError:
        raise HTTPException(status_code=401, detail="Token invalid or expired")

# ===============================
# ADMIN LOGIN (PLAIN PASSWORD)
# ===============================
@app.post("/admin/login")
def admin_login(email: str, password: str):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, password FROM admins44 WHERE official_email = %s",
        (email,)
    )

    admin = cursor.fetchone()
    cursor.close()
    conn.close()

    if not admin:
        raise HTTPException(status_code=401, detail="Invalid email")

    admin_id, stored_password = admin

    if password != stored_password:
        raise HTTPException(status_code=401, detail="Invalid password")

    token = create_access_token({
        "user_id": admin_id,
        "role": "Admin"
    })

    return {"access_token": token}

# ===============================
# EMPLOYER LOGIN (PLAIN PASSWORD)
# ===============================
@app.post("/employer/login")
def employer_login(email: str, password: str):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT employer_id, password, is_verified FROM employer_registration WHERE email_address = %s",
        (email,)
    )

    employer = cursor.fetchone()
    cursor.close()
    conn.close()

    if not employer:
        raise HTTPException(status_code=401, detail="Invalid email")

    employer_id, stored_password, is_verified = employer

    if not is_verified:
        raise HTTPException(status_code=403, detail="Account not verified")

    if password != stored_password:
        raise HTTPException(status_code=401, detail="Invalid password")

    token = create_access_token({
        "user_id": employer_id,
        "role": "Employer"
    })

    return {"access_token": token}

# ===============================
# CREATE JOB
# ===============================
@app.post("/jobs")
def create_job(job: JobCreate, user=Depends(get_current_user)):

    if user["role"] not in ["Admin", "Employer"]:
        raise HTTPException(status_code=403, detail="Not authorized")

    conn = get_connection()
    cursor = conn.cursor()

    query = """
        INSERT INTO jobs11 (
            reference_id,
            title, description, company_name, location,
            experience, industry,
            min_salary, max_salary,
            application_url,
            posted_by, posted_role
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """

    cursor.execute(query, (
        job.reference_id,
        job.title,
        job.description,
        job.company_name,
        job.location,
        job.experience,
        job.industry,
        job.min_salary,
        job.max_salary,
        job.application_url,
        user["user_id"],
        user["role"]
    ))

    conn.commit()
    cursor.close()
    conn.close()

    return {"message": "Job created successfully"}

# ===============================
# GET JOBS
# ===============================
@app.get("/jobs")
def get_jobs(user=Depends(get_current_user)):

    conn = get_connection()
    cursor = conn.cursor()

    if user["role"] == "Admin":
        cursor.execute("SELECT * FROM jobs11 ORDER BY created_at DESC")

    elif user["role"] == "Employer":
        cursor.execute(
            "SELECT * FROM jobs11 WHERE posted_by = %s AND posted_role = 'Employer' ORDER BY created_at DESC",
            (user["user_id"],)
        )

    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()
    jobs = [dict(zip(columns, row)) for row in rows]

    cursor.close()
    conn.close()

    return {"jobs": jobs}

# ===============================
# SEARCH JOBS (PUBLIC)
# ===============================
@app.get("/jobs/search")
def search_jobs(
    keyword: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    experience: Optional[str] = Query(None),
    industry: Optional[str] = Query(None),
):

    conn = get_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM jobs11 WHERE status = 'active'"
    values = []

    if keyword:
        query += " AND (LOWER(title) LIKE %s OR LOWER(description) LIKE %s)"
        values.extend([f"%{keyword.lower()}%", f"%{keyword.lower()}%"])

    if location:
        query += " AND LOWER(location) LIKE %s"
        values.append(f"%{location.lower()}%")

    if experience:
        query += " AND experience = %s"
        values.append(experience)

    if industry:
        query += " AND industry = %s"
        values.append(industry)

    query += " ORDER BY created_at DESC"

    cursor.execute(query, tuple(values))

    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()
    jobs = [dict(zip(columns, row)) for row in rows]

    cursor.close()
    conn.close()

    return {"jobs": jobs}

# ===============================
# UPDATE JOB
# ===============================
@app.put("/jobs/{job_id}")
def update_job(job_id: int, job: JobUpdate, user=Depends(get_current_user)):

    conn = get_connection()
    cursor = conn.cursor()

    update_data = job.dict(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields provided")

    fields = []
    values = []

    for key, value in update_data.items():
        fields.append(f"{key} = %s")
        values.append(value)

    values.append(job_id)

    if user["role"] == "Admin":
        query = f"""
            UPDATE jobs11
            SET {', '.join(fields)}, updated_at = NOW()
            WHERE id = %s
        """
    else:
        query = f"""
            UPDATE jobs11
            SET {', '.join(fields)}, updated_at = NOW()
            WHERE id = %s AND posted_by = %s AND posted_role = 'Employer'
        """
        values.append(user["user_id"])

    cursor.execute(query, tuple(values))
    conn.commit()

    if cursor.rowcount == 0:
        raise HTTPException(status_code=403, detail="Not authorized")

    cursor.close()
    conn.close()

    return {"message": "Job updated successfully"}

# ===============================
# DELETE JOB
# ===============================
@app.delete("/jobs/{job_id}")
def delete_job(job_id: int, user=Depends(get_current_user)):

    conn = get_connection()
    cursor = conn.cursor()

    if user["role"] == "Admin":
        cursor.execute("DELETE FROM jobs11 WHERE id = %s", (job_id,))
    else:
        cursor.execute(
            "DELETE FROM jobs11 WHERE id = %s AND posted_by = %s AND posted_role = 'Employer'",
            (job_id, user["user_id"])
        )

    conn.commit()

    if cursor.rowcount == 0:
        raise HTTPException(status_code=403, detail="Not authorized")

    cursor.close()
    conn.close()

    return {"message": "Job deleted successfully"}

@app.get("/jobs/public")
def get_public_jobs():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM jobs11 WHERE status = 'active' ORDER BY created_at DESC"
    )

    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()
    jobs = [dict(zip(columns, row)) for row in rows]

    cursor.close()
    conn.close()

    return {"jobs": jobs}

@app.get("/jobs/count")
def job_count(user=Depends(get_current_user)):

    conn = get_connection()
    cursor = conn.cursor()

    if user["role"] == "Admin":
        cursor.execute("SELECT COUNT(*) FROM jobs11")

    elif user["role"] == "Employer":
        cursor.execute(
            """
            SELECT COUNT(*) 
            FROM jobs11 
            WHERE posted_by = %s 
            AND posted_role = 'Employer'
            """,
            (user["user_id"],)
        )

    else:
        raise HTTPException(status_code=403, detail="Not authorized")

    count = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    return {"job_count": count}

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS if settings.ALLOWED_ORIGINS != [''] else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Router
app.include_router(router)

@app.get("/")
def root():
    return {"message": "API running successfully"}