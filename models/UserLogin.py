"""
Data class for user_profiles row (no SQLAlchemy - avoids Python 3.14 typing conflict).
"""
from dataclasses import dataclass


@dataclass
class UserProfile:
    """Maps to user_profiles table columns used in auth."""
    user_id: int
    email: str
    name: str
    role: str | None
    password: str
    phone_number: str | None = None
