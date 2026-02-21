"""
SQL and application models for employer_registration table.
Table definition (reference):
    employer_registration (
        employer_id, contact_person_name, company_official_name,
        email_address, password, otp, is_verified, created_at
    )
"""
from datetime import datetime
from typing import Optional

# Column names for employer_registration (for raw SQL / row mapping)
EMPLOYER_TABLE = "employer_registration"
EMPLOYER_COLUMNS = (
    "employer_id",
    "contact_person_name",
    "company_official_name",
    "email_address",
    "password",
    "otp",
    "is_verified",
    "created_at",
)


def row_to_employer_dict(row) -> dict:
    """
    Map a database row (tuple or sequence) to a dict by position.
    Order must match: employer_id, contact_person_name, company_official_name,
    email_address, password, otp, is_verified, created_at.
    """
    return {
        "employer_id": row[0],
        "contact_person_name": row[1],
        "company_official_name": row[2],
        "email_address": row[3],
        "password": row[4],
        "otp": row[5],
        "is_verified": row[6],
        "created_at": row[7],
    }
