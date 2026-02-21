"""
CRUD and auth logic: get user, verify password, OTP generation, email send, OTP verify.
Uses raw SQL with pg8000 (no SQLAlchemy).
"""
import random
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import Any

import bcrypt

from models.UserLogin import UserProfile
from utils.UserLogin import (
    SMTP_HOST,
    SMTP_PORT,
    SMTP_USER,
    SMTP_PASSWORD,
    OTP_EXPIRE_MINUTES,
    OTP_LENGTH,
)

# Columns we select for auth (order matches UserProfile)
USER_COLS = "user_id, email, name, role, password, phone_number"

# In-memory OTP store: { email: { "otp": str, "expires_at": datetime } }
_otp_store: dict[str, dict[str, Any]] = {}


def _row_to_user(row: tuple) -> UserProfile:
    """Map a result row (user_id, email, name, role, password, phone_number) to UserProfile."""
    return UserProfile(
        user_id=row[0],
        email=row[1],
        name=row[2],
        role=row[3],
        password=row[4],
        phone_number=row[5] if len(row) > 5 else None,
    )


def get_user_by_email_or_phone(conn, email_or_phone: str) -> UserProfile | None:
    """Get user by email or phone_number (for login with email/mobile)."""
    email_or_phone = email_or_phone.strip()
    # Try email first
    rows = conn.run(
        f"SELECT {USER_COLS} FROM user_profiles WHERE email = :e",
        e=email_or_phone,
    )
    if rows:
        return _row_to_user(rows[0])
    # Try phone (strip to digits)
    phone_clean = "".join(c for c in email_or_phone if c.isdigit())
    if len(phone_clean) >= 10:
        rows = conn.run(
            f"SELECT {USER_COLS} FROM user_profiles WHERE phone_number = :p",
            p=email_or_phone,
        )
        if rows:
            return _row_to_user(rows[0])
        rows = conn.run(
            f"SELECT {USER_COLS} FROM user_profiles WHERE phone_number = :p",
            p=phone_clean,
        )
        if rows:
            return _row_to_user(rows[0])
        if len(phone_clean) >= 10:
            rows = conn.run(
                f"SELECT {USER_COLS} FROM user_profiles WHERE phone_number LIKE :pat",
                pat=f"%{phone_clean}%",
            )
            if rows:
                return _row_to_user(rows[0])
    return None


def get_user_by_email(conn, email: str) -> UserProfile | None:
    """Get user by email only."""
    rows = conn.run(
        f"SELECT {USER_COLS} FROM user_profiles WHERE email = :e",
        e=email.strip(),
    )
    if rows:
        return _row_to_user(rows[0])
    return None


def verify_password(plain_password: str, stored_password: str) -> bool:
    """
    Verify password. If stored value is a bcrypt hash ($2b$/$2a$), use bcrypt.
    Otherwise allow direct match (e.g. placeholder 'temporary_hashed_password' in DB).
    """
    if not stored_password or not plain_password:
        return False
    stored = stored_password if isinstance(stored_password, str) else stored_password.decode("utf-8")
    plain = plain_password.encode("utf-8")
    # Real bcrypt hashes start with $2b$ or $2a$
    if stored.startswith("$2b$") or stored.startswith("$2a$"):
        try:
            h = stored.encode("utf-8")
            return bcrypt.checkpw(plain, h)
        except Exception:
            return False
    # Placeholder or legacy plain password in DB: compare directly
    import hmac
    return hmac.compare_digest(plain_password, stored)


def generate_otp(length: int = OTP_LENGTH) -> str:
    """Generate numeric OTP."""
    return "".join(random.choices(string.digits, k=length))


def store_otp(email: str, otp: str) -> None:
    """Store OTP for email with expiry (5 minutes)."""
    _otp_store[email.lower().strip()] = {
        "otp": otp,
        "expires_at": datetime.utcnow() + timedelta(minutes=OTP_EXPIRE_MINUTES),
    }


def get_and_validate_otp(email: str) -> tuple[bool, str | None]:
    """
    Get OTP for email. Returns (valid, otp_value).
    Valid means OTP exists and not expired. Caller must compare otp_value with user input.
    """
    key = email.lower().strip()
    if key not in _otp_store:
        return False, None
    entry = _otp_store[key]
    if datetime.utcnow() > entry["expires_at"]:
        del _otp_store[key]
        return False, None
    return True, entry["otp"]


def consume_otp(email: str) -> None:
    """Remove OTP after successful verification."""
    key = email.lower().strip()
    _otp_store.pop(key, None)


def send_otp_email(to_email: str, otp: str) -> None:
    """Send OTP to the given email using SMTP."""
    subject = "Your Login OTP - Yuvasaathi"
    body = f"""
    Hello,

    Your one-time password (OTP) for secure sign in is:

        {otp}

    This OTP is valid for {OTP_EXPIRE_MINUTES} minutes. Do not share it with anyone.

    If you did not request this, please ignore this email.

    Regards,
    Yuvasaathi Team
    """
    msg = MIMEMultipart()
    msg["From"] = SMTP_USER
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body.strip(), "plain"))

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(SMTP_USER, to_email, msg.as_string())


def authenticate_and_send_otp(conn, email_or_phone: str, password: str) -> tuple[bool, str | None]:
    """
    Verify credentials and send OTP to user's registered email.
    Returns (success, error_message). On success, error_message is None.
    """
    user = get_user_by_email_or_phone(conn, email_or_phone)
    if not user:
        return False, "Invalid email/mobile or password."
    if not verify_password(password, user.password):
        return False, "Invalid email/mobile or password."
    otp = generate_otp()
    store_otp(user.email, otp)
    try:
        send_otp_email(user.email, otp)
    except Exception as e:
        consume_otp(user.email)
        return False, f"Failed to send OTP: {str(e)}"
    return True, None


def verify_otp_and_get_user(conn, email: str, otp: str) -> UserProfile | None:
    """
    Verify OTP for email. If valid, consume OTP and return user; else return None.
    """
    user = get_user_by_email(conn, email)
    if not user:
        return None
    valid, stored_otp = get_and_validate_otp(email)
    if not valid or stored_otp != otp:
        return None
    consume_otp(email)
    return user
