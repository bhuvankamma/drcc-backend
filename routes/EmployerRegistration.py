from fastapi import APIRouter, Depends, HTTPException

import pg8000.dbapi

from crud.EmployerRegistration import (
    get_employer_id_by_email,
    get_employer_by_email,
    create_employer,
    set_verified_and_clear_otp,
    update_otp,
    update_password_and_clear_otp,
    fetchone_dict,
)
from database.database import get_db
from schemas.EmployerRegistration import (
    EmployerCreate,
    ForgotPasswordRequest,
    OTPVerify,
    ResetPassword,
)
from utils.RegistrationEmployer import generate_otp, hash_password, send_email

router = APIRouter()


@router.get("/")
def home():
    return {
        "message": "Employer Registration API is running",
        "docs": "/docs",
    }


@router.get("/health")
def health(db: pg8000.dbapi.Connection = Depends(get_db)):
    cur = db.cursor()
    try:
        cur.execute("SELECT 1 AS ok")
        row = fetchone_dict(cur)
        return {"ok": bool(row and row.get("ok") == 1)}
    finally:
        cur.close()


@router.post("/employee_register")
def register_employer(data: EmployerCreate, db: pg8000.dbapi.Connection = Depends(get_db)):
    existing_id = get_employer_id_by_email(db, str(data.email_address))
    if existing_id is not None:
        raise HTTPException(status_code=400, detail="Employer already registered")

    if data.password != data.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    otp = generate_otp()
    hashed_pw = hash_password(data.password)
    create_employer(
        db,
        data.contact_person_name,
        data.company_official_name,
        str(data.email_address),
        hashed_pw,
        otp,
    )
    send_email(data.email_address, "Employer Registration OTP", f"Your OTP is {otp}")
    return {"message": "OTP sent to email for verification."}


@router.post("/verify_otp")
def verify_otp(data: OTPVerify, db: pg8000.dbapi.Connection = Depends(get_db)):
    employer = get_employer_by_email(db, str(data.email_address))
    if not employer:
        raise HTTPException(status_code=404, detail="Employer not found")

    if (employer.get("otp") or "") != data.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    set_verified_and_clear_otp(db, employer["employer_id"])
    return {"message": "Email verified successfully!"}


@router.post("/forgot_password")
def forgot_password(data: ForgotPasswordRequest, db: pg8000.dbapi.Connection = Depends(get_db)):
    employer = get_employer_by_email(db, str(data.email_address))
    if not employer:
        raise HTTPException(status_code=404, detail="Email not found")

    otp = generate_otp()
    update_otp(db, employer["employer_id"], otp)
    send_email(data.email_address, "Password Reset OTP", f"Your password reset OTP is {otp}")
    return {"message": "Password reset OTP sent to your email."}


@router.post("/reset_password")
def reset_password(data: ResetPassword, db: pg8000.dbapi.Connection = Depends(get_db)):
    employer = get_employer_by_email(db, str(data.email_address))
    if not employer:
        raise HTTPException(status_code=404, detail="Employer not found")

    if (employer.get("otp") or "") != data.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    if data.new_password != data.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    update_password_and_clear_otp(db, employer["employer_id"], hash_password(data.new_password))
    return {"message": "Password reset successfully!"}
