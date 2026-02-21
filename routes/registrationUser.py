"""API routes: registration, users, lookup."""
import logging

from fastapi import APIRouter, HTTPException, Path, Query, Depends
from sqlalchemy.orm import Session

from crud import create_user, get_user_by_id as crud_get_user_by_id, get_user_by_email as crud_get_user_by_email
from schemas import ApplicantRegister, UserResponse, LookupItem
from utils.Registrationauth import hash_password
from database.database import get_db

logger = logging.getLogger(__name__)
router = APIRouter()
DEFAULT_ROLE = "Employee"


@router.post(
    "/registration/register",
    response_model=UserResponse,
    summary="Register new applicant",
    responses={400: {"description": "Email already registered or validation error"}},
)
def register_applicant(body: ApplicantRegister, db: Session = Depends(get_db)):
    name = f"{body.first_name} {body.middle_name or ''} {body.surname}".strip()
    phone_number = f"{body.country_code}{body.mobile_number}" if body.country_code else body.mobile_number
    department = f"{body.preferred_sector} - {body.preferred_job_role}"
    try:
        user = create_user(
            db=db,
            email=body.email,
            name=name,
            role=DEFAULT_ROLE,
            password_hash=hash_password(body.password),
            phone_number=phone_number,
            company_name=None,
            department=department,
            address=body.current_state,
            previous_ctc=None,
            expected_ctc=None,
            notice_period=None,
            field_of_work=department,
            education=body.highest_qualification,
            experience=body.employment_history or None,
            skills=body.certifications_skills or None,
        )
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Registration failed")
        err_msg = str(e).lower()
        if "unique" in err_msg and "email" in err_msg:
            raise HTTPException(status_code=400, detail="Email already registered")
        raise HTTPException(status_code=500, detail=f"Registration failed: {e!s}")


@router.get("/users/by-email/", response_model=UserResponse, responses={404: {"description": "User not found"}})
def get_user_by_email(
    email: str = Query(..., examples=["rahul.sharma@example.com"], description="User's email"),
    db: Session = Depends(get_db),
):
    user = crud_get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/users/{user_id}", response_model=UserResponse, responses={404: {"description": "User not found"}})
def get_user_by_id(user_id: int = Path(..., examples=[1], description="User ID"), db: Session = Depends(get_db)):
    user = crud_get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


QUALIFICATIONS = [
    "Below 10th", "10th / Matric", "12th / Intermediate", "ITI", "Diploma",
    "Graduate", "Post Graduate", "Professional Degree", "PhD", "Other",
]
INDIAN_STATES = [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
    "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka",
    "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram",
    "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu",
    "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal",
    "Delhi", "Jammu and Kashmir", "Ladakh", "Puducherry", "Chandigarh", "Other",
]
SECTORS = [
    "Government", "IT / Software", "Banking & Finance", "Healthcare", "Education",
    "Manufacturing", "Retail", "Construction", "Agriculture", "Logistics",
    "Hospitality", "Media", "NGO / Social", "Other",
]
JOB_ROLES = [
    "Software Developer", "Data Analyst", "Accountant", "Teacher", "Nurse",
    "Engineer", "Clerk", "Driver", "Electrician", "Mechanic", "Admin",
    "HR", "Sales", "Marketing", "Customer Support", "Other",
]


def _to_items(values: list) -> list:
    return [LookupItem(id=v, label=v) for v in values]


@router.get("/lookup/qualifications", response_model=list[LookupItem])
def list_qualifications():
    return _to_items(QUALIFICATIONS)


@router.get("/lookup/states", response_model=list[LookupItem])
def list_states():
    return _to_items(INDIAN_STATES)


@router.get("/lookup/sectors", response_model=list[LookupItem])
def list_sectors():
    return _to_items(SECTORS)


@router.get("/lookup/job-roles", response_model=list[LookupItem])
def list_job_roles():
    return _to_items(JOB_ROLES)
