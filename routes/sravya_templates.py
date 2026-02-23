from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.database import get_db
from models import resume_template
from schemas import resume_template_schema

router = APIRouter(prefix="/templates", tags=["Templates"])


@router.get("/", response_model=list[resume_template_schema.TemplateResponse])
def get_templates(db: Session = Depends(get_db)):
    return db.query(resume_template_schema.Template).all()