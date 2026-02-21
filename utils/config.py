"""App config / settings."""
import os
from pathlib import Path

# Default user id when auth is not in use (e.g. dev)
default_user_id = os.environ.get("DEFAULT_USER_ID", "1")

# Max upload size: 10 MB
max_upload_mb = int(os.environ.get("MAX_UPLOAD_MB", "10"))
max_upload_bytes = max_upload_mb * 1024 * 1024

# Base dir for resume uploads (optional override)
BASE_DIR = Path(__file__).resolve().parent.parent
resume_upload_dir = Path(os.environ.get("RESUME_UPLOAD_DIR", str(BASE_DIR / "uploads" / "resumes")))


class _Settings:
    default_user_id: str = default_user_id
    max_upload_mb: int = max_upload_mb
    max_upload_bytes: int = max_upload_bytes
    resume_upload_dir: Path = resume_upload_dir


settings = _Settings()
