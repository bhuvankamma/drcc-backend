"""User CRUD: create_user, get_user_by_id, get_user_by_email."""
from typing import Optional
from sqlalchemy.orm import Session
from models.user_profile import UserProfile


def create_user(
    db: Session,
    email: str,
    name: str,
    role: str,
    password_hash: str,
    phone_number: Optional[str] = None,
    company_name: Optional[str] = None,
    department: Optional[str] = None,
    address: Optional[str] = None,
    previous_ctc: Optional[str] = None,
    expected_ctc: Optional[str] = None,
    notice_period: Optional[str] = None,
    field_of_work: Optional[str] = None,
    education: Optional[str] = None,
    experience: Optional[str] = None,
    skills: Optional[str] = None,
):
    user = UserProfile(
        email=email,
        name=name,
        role=role,
        password=password_hash,
        phone_number=phone_number,
        company_name=company_name,
        department=department,
        address=address,
        previous_ctc=previous_ctc,
        expected_ctc=expected_ctc,
        notice_period=notice_period,
        field_of_work=field_of_work,
        education=education,
        experience=experience,
        skills=skills,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def get_user_by_id(db: Session, user_id: int) -> Optional[UserProfile]:
    return db.query(UserProfile).filter(UserProfile.user_id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[UserProfile]:
    return db.query(UserProfile).filter(UserProfile.email == email).first()
