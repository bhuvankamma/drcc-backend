"""CRUD for resume uploads: file storage + JSON metadata."""
import json
import re
import uuid
from datetime import datetime
from pathlib import Path

from utils.config import settings

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc"}
META_FILE = "resume_meta.json"


def _meta_path() -> Path:
    d = settings.resume_upload_dir
    d.mkdir(parents=True, exist_ok=True)
    return d / META_FILE


def _load_meta() -> list[dict]:
    p = _meta_path()
    if not p.exists():
        return []
    try:
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def _save_meta(meta: list[dict]) -> None:
    _meta_path().parent.mkdir(parents=True, exist_ok=True)
    with open(_meta_path(), "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)


def _safe_filename(name: str) -> str:
    return re.sub(r"[^\w.\-]", "_", name or "file")[:200]


def is_allowed_file(filename: str) -> bool:
    if not filename or not filename.strip():
        return False
    ext = Path(filename).suffix.lower()
    return ext in ALLOWED_EXTENSIONS


def list_resumes(user_id: int) -> list[dict]:
    meta = _load_meta()
    return [m for m in meta if m.get("user_id") == user_id]


def save_upload(*, file_content: bytes, original_filename: str, user_id: int) -> dict:
    ext = Path(original_filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"File type not allowed. Allowed: PDF, DOCX, DOC")
    rid = uuid.uuid4().hex[:12]
    safe = _safe_filename(Path(original_filename).stem) + ext
    store_name = f"{rid}_{safe}"
    dest_dir = settings.resume_upload_dir
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / store_name
    dest.write_bytes(file_content)
    now = datetime.utcnow().isoformat() + "Z"
    meta = _load_meta()
    rec = {
        "id": len(meta) + 1,
        "user_id": user_id,
        "filename": original_filename,
        "file_type": ext.lstrip(".").upper(),
        "upload_date": now,
        "store_name": store_name,
    }
    meta.append(rec)
    _save_meta(meta)
    return {
        "id": rec["id"],
        "filename": rec["filename"],
        "upload_date": rec["upload_date"],
        "file_type": rec["file_type"],
    }


def get_resume_file_content(resume_id: int, user_id: int) -> tuple[bytes, str] | None:
    meta = _load_meta()
    for m in meta:
        if m.get("id") == resume_id and m.get("user_id") == user_id:
            store_name = m.get("store_name")
            if not store_name:
                return None
            path = settings.resume_upload_dir / store_name
            if not path.exists():
                return None
            return path.read_bytes(), m.get("filename", store_name)
    return None


def update_resume_metadata(resume_id: int, filename: str, user_id: int) -> dict | None:
    meta = _load_meta()
    for m in meta:
        if m.get("id") == resume_id and m.get("user_id") == user_id:
            m["filename"] = filename
            _save_meta(meta)
            return {
                "id": m["id"],
                "filename": m["filename"],
                "upload_date": m["upload_date"],
                "file_type": m["file_type"],
            }
    return None


def delete_resume(resume_id: int, user_id: int) -> bool:
    meta = _load_meta()
    for i, m in enumerate(meta):
        if m.get("id") == resume_id and m.get("user_id") == user_id:
            store_name = m.get("store_name")
            if store_name:
                path = settings.resume_upload_dir / store_name
                if path.exists():
                    path.unlink(missing_ok=True)
            meta.pop(i)
            _save_meta(meta)
            return True
    return False
