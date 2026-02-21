"""Resume & Document Management API routes."""
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import Response

from crud import resume, resume_builder
from schemas.resume import (
    ResumeBuilderIn,
    ResumeBuilderOut,
    ResumeOut,
    ResumeUpdateIn,
    ResumeUploadResponse,
)
from utils.config import settings

router = APIRouter(prefix="/resumes", tags=["resumes"])


def get_current_user_id() -> int:
    raw = settings.default_user_id or "1"
    try:
        return int(raw.strip())
    except ValueError:
        return 1


@router.get("", response_model=list[ResumeOut])
def list_resumes(user_id: int = Depends(get_current_user_id)):
    items = resume.list_resumes(user_id=user_id)
    return [ResumeOut(**x) for x in items]


@router.post("/upload", response_model=ResumeUploadResponse)
async def upload_resume(
    file: UploadFile = File(...),
    user_id: int = Depends(get_current_user_id),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    if not resume.is_allowed_file(file.filename):
        raise HTTPException(status_code=400, detail="File type not allowed. Allowed: PDF, DOCX, DOC")
    content = await file.read()
    if len(content) > settings.max_upload_bytes:
        raise HTTPException(status_code=400, detail=f"File too large. Max size: {settings.max_upload_mb} MB")
    try:
        rec = resume.save_upload(file_content=content, original_filename=file.filename, user_id=user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    return ResumeUploadResponse(
        id=rec["id"],
        filename=rec["filename"],
        upload_date=rec["upload_date"],
        file_type=rec["file_type"],
    )


@router.get("/builder", response_model=ResumeBuilderOut | None)
def get_resume_builder_route(user_id: int = Depends(get_current_user_id)):
    rec = resume_builder.get_resume_builder(user_id=user_id)
    return ResumeBuilderOut(**rec) if rec else None


@router.post("/builder", response_model=ResumeBuilderOut)
def save_resume_builder_route(body: ResumeBuilderIn, user_id: int = Depends(get_current_user_id)):
    data = body.model_dump()
    rec = resume_builder.save_resume_builder(user_id=user_id, data=data)
    return ResumeBuilderOut(**rec)


@router.get("/{resume_id}/download")
def download_resume(resume_id: int, user_id: int = Depends(get_current_user_id)):
    result = resume.get_resume_file_content(resume_id, user_id=user_id)
    if not result:
        raise HTTPException(status_code=404, detail="Resume not found")
    content, filename = result
    return Response(
        content=content,
        media_type="application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.patch("/{resume_id}", response_model=ResumeOut)
def update_resume(resume_id: int, body: ResumeUpdateIn, user_id: int = Depends(get_current_user_id)):
    if body.filename is None:
        raise HTTPException(status_code=400, detail="No filename provided")
    rec = resume.update_resume_metadata(resume_id=resume_id, filename=body.filename, user_id=user_id)
    if not rec:
        raise HTTPException(status_code=404, detail="Resume not found")
    return ResumeOut(**rec)


@router.delete("/{resume_id}", status_code=204)
def delete_resume(resume_id: int, user_id: int = Depends(get_current_user_id)):
    if not resume.delete_resume(resume_id, user_id=user_id):
        raise HTTPException(status_code=404, detail="Resume not found")
    return None
