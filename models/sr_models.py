from sqlalchemy import Column, Integer, String
from database.sr_database import Base


class Recruiter(Base):
    __tablename__ = "recruiters"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))
    email = Column(String(255), unique=True)
    role = Column(String(100))
    company_name = Column(String(255))
    invite_token = Column(String(255), nullable=True)