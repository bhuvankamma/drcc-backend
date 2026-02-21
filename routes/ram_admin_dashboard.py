from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from database.database import get_db

router = APIRouter(
    prefix="/admin",
    tags=["Admin Dashboard"]
)


@router.get("/dashboard")
def get_dashboard(db: Session = Depends(get_db)):

    query = text("""

        SELECT
            (SELECT COUNT(*) FROM user_profiles) AS total_users,

            (SELECT COUNT(*) 
             FROM jobs11 
             WHERE status = 'active') AS active_jobs,

            -- FUTURE: Uncomment when table exists
            -- (SELECT COUNT(*) FROM job_applications) AS total_applications,

            -- FUTURE: Uncomment when table exists
            -- (SELECT COUNT(*) FROM skill_programs) AS total_programs

            0 AS total_applications,
            0 AS total_programs

    """)

    result = db.execute(query).fetchone()

    return {
        "total_users": result.total_users,
        "active_jobs": result.active_jobs,
        "total_applications": result.total_applications,
        "total_programs": result.total_programs
    }