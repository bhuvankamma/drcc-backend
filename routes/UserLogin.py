"""
Auth API routes: generate OTP (login), verify OTP, and return JWT.
"""
from datetime import datetime, timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from jose import jwt

from database import get_db
from schemas import (
    LoginRequest,
    GenerateOTPResponse,
    VerifyOTPRequest,
    TokenResponse,
)
from crud import (
    authenticate_and_send_otp,
    get_user_by_email_or_phone,
    verify_otp_and_get_user,
)
from utils.UserLogin import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter(prefix="/api/auth", tags=["auth"])


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


@router.post("/generate-otp", response_model=GenerateOTPResponse)
def generate_otp(request: LoginRequest, conn: Any = Depends(get_db)):
    """
    Verify email/mobile and password, then send OTP to the user's registered email.
    """
    success, error = authenticate_and_send_otp(conn, request.email, request.password)
    if not success:
        raise HTTPException(status_code=401, detail=error)
    user = get_user_by_email_or_phone(conn, request.email)
    return GenerateOTPResponse(
        message="OTP sent to your registered email. Valid for 5 minutes.",
        email=user.email,
    )


@router.post("/verify-otp", response_model=TokenResponse)
def verify_otp(request: VerifyOTPRequest, conn: Any = Depends(get_db)):
    """
    Verify OTP and return JWT access token.
    """
    user = verify_otp_and_get_user(conn, request.email, request.otp)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired OTP.")
    token = create_access_token(
        data={"sub": user.email, "user_id": user.user_id},
    )
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user_id=user.user_id,
        email=user.email,
        name=user.name,
        role=user.role,
    )
