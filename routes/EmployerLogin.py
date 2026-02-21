"""
FastAPI router for employer login.
"""
from fastapi import APIRouter, HTTPException, status

from schemas.EmployerLogin import EmployerLoginRequest, EmployerLoginResponse
from crud.EmployerLogin import authenticate_employer

router = APIRouter(prefix="/employer", tags=["Employer Login"])


@router.post("/login", response_model=EmployerLoginResponse)
def employer_login(payload: EmployerLoginRequest):
    """
    Employer login: validate email and password.
    Returns employer info (no password) on success; 401 if invalid credentials.
    """
    employer = authenticate_employer(
        email_address=payload.email_address,
        password=payload.password,
    )
    if not employer:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    return EmployerLoginResponse(
        message="Login successful",
        employer_id=employer["employer_id"],
        contact_person_name=employer["contact_person_name"],
        company_official_name=employer["company_official_name"],
        email_address=employer["email_address"],
    )
