from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from database.database import get_db
from models.user_profile import UserProfile
from schemas.user_profile import ProfileUpdateSchema

app = FastAPI()


# ----------------------------------------
# GET PROFILE (Dashboard Load)
# ----------------------------------------
@app.get("/profile/{user_id}")
def get_profile(user_id: int, db: Session = Depends(get_db)):

    user = db.query(UserProfile).filter(
        UserProfile.user_id == user_id
    ).first()

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return {
        "user_id": user.user_id,
        "email": user.email,
        "name": user.name,
        "role": user.role,
        "phone_number": user.phone_number,
        "company_name": user.company_name,
        "department": user.department,
        "address": user.address,
        "previous_ctc": user.previous_ctc,
        "expected_ctc": user.expected_ctc,
        "notice_period": user.notice_period,
        "field_of_work": user.field_of_work,
        "education": user.education,
        "experience": user.experience,
        "skills": user.skills
    }


# ----------------------------------------
# UPDATE PROFILE (Edit Profile Save)
# ----------------------------------------
@app.put("/profile/{user_id}")
def update_profile(
    user_id: int,
    data: ProfileUpdateSchema,
    db: Session = Depends(get_db)
):

    user = db.query(UserProfile).filter(
        UserProfile.user_id == user_id
    ).first()

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # Update only editable fields
    user.address = data.address
    user.previous_ctc = data.previous_ctc
    user.expected_ctc = data.expected_ctc
    user.notice_period = data.notice_period
    user.field_of_work = data.field_of_work
    user.education = data.education
    user.experience = data.experience
    user.skills = data.skills

    db.commit()
    db.refresh(user)

    return {
        "message": "Profile updated successfully",
        "user_id": user.user_id
    }

#===================sravya resume template===========

from fastapi import FastAPI
from sqlalchemy.orm import Session
from database.database import engine, SessionLocal
from models import resume_template
from routes import sravya_templates, sravya_resumes

resume_template.Base.metadata.create_all(bind=engine)

#app = FastAPI(title="Resume Backend API")

app.include_router(sravya_templates.router)
app.include_router(sravya_resumes.router)


def seed_templates():
    db: Session = SessionLocal()
    if db.query(resume_template.Template).first():
        db.close()
        return

    templates_data = [
        resume_template.Template(name="Standard Professional", description="Clean and classic corporate resume", preview_url="standard.png"),
        resume_template.Template(name="Modern & Creative", description="Stylish resume with colored sections", preview_url="modern.png"),
        resume_template.Template(name="Minimalist Design", description="Simple and elegant resume layout", preview_url="minimal.png"),
        resume_template.Template(name="Academic & Research", description="Detailed academic CV format", preview_url="academic.png"),
    ]

    db.add_all(templates_data)
    db.commit()
    db.close()


seed_templates()


@app.get("/")
def root():
    return {"message": "Resume Backend Running 🚀"}