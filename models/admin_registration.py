from sqlalchemy import Column, Integer, String, DateTime, func
from database.database import Base

class Admin(Base):
    __tablename__ = "admins44"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(150), nullable=False)
    department = Column(String(100), nullable=False)
    designation = Column(String(100), nullable=False)
    govt_id = Column(String(50), unique=True, nullable=False)
    mobile_number = Column(String(20), nullable=False)
    official_email = Column(String(150), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
