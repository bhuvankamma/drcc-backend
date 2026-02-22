import os
from dotenv import load_dotenv
from pathlib import Path

# Load .env from app folder
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


class Settings:
    # Database Config
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_NAME = os.getenv("DB_NAME", "postgres")

    DATABASE_URL = (
        f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}"
        f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    # CORS
    ALLOWED_ORIGINS = (
        os.getenv("ALLOWED_ORIGINS", "*").split(",")
        if os.getenv("ALLOWED_ORIGINS")
        else ["*"]
    )

    # Email Config
    SENDER_EMAIL = os.getenv("SENDER_EMAIL")
    SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")

    # Debug check (remove later)
    def validate(self):
        if not self.SENDER_EMAIL or not self.SENDER_PASSWORD:
            print("⚠ WARNING: Email credentials not loaded from .env")


settings = Settings()
settings.validate()