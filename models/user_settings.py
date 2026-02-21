from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from database.database import Base


class User(Base):
    __tablename__ = "user_profiles"
    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    role = Column(String(50), nullable=True)  # Admin / Employer / Employee
    password = Column(String(255), nullable=False)  # store hashed password (bcrypt)
    phone_number = Column(String(50), nullable=True)
    company_name = Column(String(255), nullable=True)
    department = Column(String(255), nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    address = Column(String(500), nullable=True)
    previous_ctc = Column(String(100), nullable=True)
    expected_ctc = Column(String(100), nullable=True)
    notice_period = Column(String(100), nullable=True)
    field_of_work = Column(String(255), nullable=True)
    education = Column(String(255), nullable=True)
    experience = Column(String, nullable=True)  # TEXT
    skills = Column(String, nullable=True)  # TEXT
    profile_picture = Column(String(500), nullable=True)  # URL or path for profile image
