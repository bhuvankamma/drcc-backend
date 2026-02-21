from sqlalchemy.orm import Session
from models.user_settings import User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.user_id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def create_user(db: Session, user):
    hashed_password = pwd_context.hash(user.password)
    db_user = User(
        email=user.email,
        name=user.name,
        role=user.role,
        password=hashed_password,
        phone_number=user.phone_number,
        company_name=user.company_name,
        department=user.department,
        address=user.address,
        previous_ctc=user.previous_ctc,
        expected_ctc=user.expected_ctc,
        notice_period=user.notice_period,
        field_of_work=user.field_of_work,
        education=user.education,
        experience=user.experience,
        skills=user.skills,
        profile_picture=getattr(user, "profile_picture", None),
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user_id: int, user_data):
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    for key, value in user_data.model_dump(exclude_unset=True).items():
        setattr(db_user, key, value)
    db.commit()
    db.refresh(db_user)
    return db_user


def change_password(db: Session, user_id: int, new_password: str):
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    db_user.password = pwd_context.hash(new_password)
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int):
    db_user = get_user(db, user_id)
    if db_user:
        db.delete(db_user)
        db.commit()
