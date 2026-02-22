"""App configuration. Set these via environment or .env file."""
import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME", "your_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

# Table name for admin registration (admins44)
ADMIN_TABLE = os.getenv("ADMIN_TABLE", "admins44")

# Directory for uploaded profile pictures
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
# URL prefix for serving uploads (e.g. /uploads/)
UPLOAD_URL_PREFIX = "/uploads/"
