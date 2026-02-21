"""
CRUD operations for employer login (find by email, verify password).
"""
from passlib.context import CryptContext
from typing import Optional

from database import get_db
from models.EmployerLogin import EMPLOYER_TABLE, row_to_employer_dict

# Password hashing context (must match how passwords were stored at registration)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_employer_by_email(conn, email_address: str) -> Optional[dict]:
    """
    Fetch a single employer by email_address.
    Returns None if not found, else a dict with employer fields.
    """
    rows = conn.run(
        "SELECT employer_id, contact_person_name, company_official_name,"
        " email_address, password, otp, is_verified, created_at"
        f" FROM {EMPLOYER_TABLE} WHERE email_address = :email",
        email=email_address.strip().lower(),
    )
    if not rows:
        return None
    return row_to_employer_dict(rows[0])


def verify_password(plain_password: str, stored_password: str) -> bool:
    """
    Verify plain password against stored value.
    Supports bcrypt hashes; falls back to plain comparison if not a valid hash
    (e.g. if registration stored plain passwords).
    """
    try:
        return pwd_context.verify(plain_password, stored_password)
    except Exception:
        return plain_password == stored_password


def authenticate_employer(email_address: str, password: str) -> Optional[dict]:
    """
    Authenticate employer by email and password.
    Uses get_db() to get a connection, finds employer by email,
    verifies password (bcrypt). Optionally enforce is_verified.
    Returns employer dict (without password) on success, None on failure.
    """
    with get_db() as conn:
        employer = get_employer_by_email(conn, email_address)
        if not employer:
            return None
        if not verify_password(password, employer["password"]):
            return None
        # Optional: require verified account for login
        # if not employer.get("is_verified"):
        #     return None
        # Remove password from returned data
        out = {k: v for k, v in employer.items() if k != "password"}
        return out
