from sqlalchemy.orm import Session
from models.sr_models import Recruiter
import uuid


# ---------------- CREATE RECRUITER ----------------

def create_recruiter(db: Session, name: str, email: str, role: str, company_name: str):
    token = str(uuid.uuid4())

    recruiter = Recruiter(
        name=name,
        email=email,
        role=role,
        company_name=company_name,
        invite_token=token
    )

    db.add(recruiter)
    db.commit()
    db.refresh(recruiter)

    return recruiter, token


# ---------------- GET ALL INVITES (ADMIN) ----------------

def get_all_recruiters(db: Session):
    return db.query(Recruiter).order_by(Recruiter.id.desc()).all()


# ---------------- GET RECRUITER BY TOKEN ----------------

def get_recruiter_by_token(db: Session, token: str):
    return db.query(Recruiter).filter(
        Recruiter.invite_token == token
    ).first()


# ---------------- GET RECRUITER BY EMAIL ----------------

def get_recruiter_by_email(db: Session, email: str):
    return db.query(Recruiter).filter(
        Recruiter.email == email
    ).first()


# ---------------- DELETE RECRUITER ----------------

def delete_recruiter(db: Session, recruiter_id: int):
    recruiter = db.query(Recruiter).filter(
        Recruiter.id == recruiter_id
    ).first()

    if recruiter:
        db.delete(recruiter)
        db.commit()

    return recruiter