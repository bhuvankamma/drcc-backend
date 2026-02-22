from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from database.database import Base


class Admin(Base):
    __tablename__ = "admins44"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=True)
    department = Column(String, nullable=True)
    designation = Column(String, nullable=True)
    govt_id = Column(String, nullable=True)
    mobile_number = Column(String, nullable=True)
    official_email = Column(String, nullable=True, index=True)
    password = Column(String, nullable=True)
    profile_picture_url = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String, nullable=True)
