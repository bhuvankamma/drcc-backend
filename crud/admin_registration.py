# app/core/security.py

import re
from datetime import datetime, timedelta
from typing import Optional

from passlib.context import CryptContext
from jose import JWTError, jwt


# ================= PASSWORD HASHING =================

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# ================= PASSWORD VALIDATION =================

class PasswordValidationError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


def validate_password_strength(password: str) -> None:
    """
    Enforces:
    - Minimum 8 characters
    - At least one uppercase
    - At least one lowercase
    - At least one digit
    - At least one special character
    """

    if len(password) < 8:
        raise PasswordValidationError(
            "Password must be at least 8 characters long."
        )

    if not re.search(r"[A-Z]", password):
        raise PasswordValidationError(
            "Password must contain at least one uppercase letter."
        )

    if not re.search(r"[a-z]", password):
        raise PasswordValidationError(
            "Password must contain at least one lowercase letter."
        )

    if not re.search(r"[0-9]", password):
        raise PasswordValidationError(
            "Password must contain at least one digit."
        )

    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        raise PasswordValidationError(
            "Password must contain at least one special character."
        )


# ================= JWT CONFIG (OPTIONAL BUT RECOMMENDED) =================

SECRET_KEY = "your-secret-key-change-this"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None