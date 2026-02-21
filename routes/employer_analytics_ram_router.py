from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.database import get_db
from utils.employer_analytics_ram_service import (
    get_job_postings_per_month,
    get_recruiter_activity,
    # get_industry_distribution
)

router = APIRouter(
    prefix="/Employer analytics",
    tags=["Employer Analytics"]
)


# Line Chart API
@router.get("/job-postings")
def job_postings(db: Session = Depends(get_db)):
    return get_job_postings_per_month(db)


# Bar Chart API
@router.get("/recruiter-activity")
def recruiter_activity(db: Session = Depends(get_db)):
    return get_recruiter_activity(db)


# Pie Chart API
# COMMENTED because not present in UI
# Remove comments if needed

"""
@router.get("/industry-distribution")
def industry_distribution(db: Session = Depends(get_db)):
    return get_industry_distribution(db)
"""