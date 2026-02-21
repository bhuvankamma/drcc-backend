"""User CRUD: create_user, get_user_by_id, get_user_by_email."""
from typing import Optional

from database.database import db_cursor, commit

USER_SELECT = (
    "user_id, email, name, role, phone_number, company_name, department, "
    "address, previous_ctc, expected_ctc, notice_period, field_of_work, "
    "education, experience, skills, created_at"
)


def _row_to_dict(r) -> dict:
    return {
        "user_id": r[0], "email": r[1], "name": r[2], "role": r[3],
        "phone_number": r[4], "company_name": r[5], "department": r[6],
        "address": r[7], "previous_ctc": r[8], "expected_ctc": r[9],
        "notice_period": r[10], "field_of_work": r[11], "education": r[12],
        "experience": r[13], "skills": r[14], "created_at": r[15],
    }


def create_user(email: str, name: str, role: str, password_hash: str,
                phone_number: Optional[str] = None, company_name: Optional[str] = None,
                department: Optional[str] = None, address: Optional[str] = None,
                previous_ctc: Optional[str] = None, expected_ctc: Optional[str] = None,
                notice_period: Optional[str] = None, field_of_work: Optional[str] = None,
                education: Optional[str] = None, experience: Optional[str] = None,
                skills: Optional[str] = None) -> dict:
    with db_cursor() as conn:
        conn.run(
            """
            INSERT INTO user_profiles (
                email, name, role, password, phone_number, company_name, department,
                address, previous_ctc, expected_ctc, notice_period, field_of_work,
                education, experience, skills
            ) VALUES (
                :email, :name, :role, :password, :phone_number, :company_name, :department,
                :address, :previous_ctc, :expected_ctc, :notice_period, :field_of_work,
                :education, :experience, :skills
            )
            """,
            email=email, name=name, role=role, password=password_hash,
            phone_number=phone_number, company_name=company_name, department=department,
            address=address, previous_ctc=previous_ctc, expected_ctc=expected_ctc,
            notice_period=notice_period, field_of_work=field_of_work,
            education=education, experience=experience, skills=skills,
        )
        commit(conn)
        rows = conn.run(f"SELECT {USER_SELECT} FROM user_profiles WHERE email = :email", email=email)
    if not rows:
        raise RuntimeError("Registration failed")
    return _row_to_dict(rows[0])


def get_user_by_id(user_id: int) -> Optional[dict]:
    with db_cursor() as conn:
        rows = conn.run(f"SELECT {USER_SELECT} FROM user_profiles WHERE user_id = :user_id", user_id=user_id)
    return _row_to_dict(rows[0]) if rows else None


def get_user_by_email(email: str) -> Optional[dict]:
    with db_cursor() as conn:
        rows = conn.run(f"SELECT {USER_SELECT} FROM user_profiles WHERE email = :email", email=email)
    return _row_to_dict(rows[0]) if rows else None
