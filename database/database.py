from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import logging

 
load_dotenv()

DATABASE_URL = "postgresql://postgres:Ram%40123@localhost:5432/postgres"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

def get_connection():
    return engine.raw_connection()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
