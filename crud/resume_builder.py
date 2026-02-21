"""CRUD for resume builder (per-user JSON data)."""
import json
from pathlib import Path

from utils.config import settings

BUILDER_FILE = "resume_builder.json"


def _builder_path(user_id: int) -> Path:
    d = settings.resume_upload_dir
    d.mkdir(parents=True, exist_ok=True)
    return d / f"builder_{user_id}.json"


def get_resume_builder(user_id: int) -> dict | None:
    p = _builder_path(user_id)
    if not p.exists():
        return None
    try:
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None


def save_resume_builder(user_id: int, data: dict) -> dict:
    p = _builder_path(user_id)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    return data
