from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.responses import FileResponse
from database.database import get_db
from models import resume_template
from schemas import resume_template_schema
from services.pdf_generator import generate_pdf
import json

router = APIRouter(prefix="/resumes", tags=["Resumes"])


@router.post("/", response_model=resume_template_schema.ResumeResponse)
def create_resume(resume: resume_template_schema.ResumeCreate, db: Session = Depends(get_db)):
    resume_json = json.dumps(resume.resume_data)

    new_resume = resume_template.Resume(
        user_id=resume.user_id,
        template_id=resume.template_id,
        resume_data=resume_json
    )

    db.add(new_resume)
    db.commit()
    db.refresh(new_resume)

    return new_resume


@router.get("/generate/{resume_id}")
def generate_resume_pdf(resume_id: int, db: Session = Depends(get_db)):
    resume = db.query(resume_template.Resume).filter(resume_template.Resume.id == resume_id).first()

    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    file_path = generate_pdf(resume)

    return FileResponse(
        file_path,
        media_type='application/pdf',
        filename=f"resume_{resume.id}.pdf"
    )