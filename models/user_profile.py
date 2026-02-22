from sqlalchemy import Column, Integer, String, Text, TIMESTAMP
from sqlalchemy.sql import func
from database.database import Base


class UserProfile(Base):

    __tablename__ = "user_profiles"

    user_id = Column(Integer, primary_key=True, index=True)

    email = Column(String, unique=True, nullable=False)

    name = Column(String, nullable=False)

    role = Column(String)

    password = Column(String, nullable=False)

    phone_number = Column(String)

    company_name = Column(String)

    department = Column(String)

    created_at = Column(TIMESTAMP, server_default=func.now())

    address = Column(String)

    previous_ctc = Column(String)

    expected_ctc = Column(String)

    notice_period = Column(String)

    field_of_work = Column(String)

    education = Column(String)

    experience = Column(Text)

    skills = Column(Text)
