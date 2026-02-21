from sqlalchemy import Column, Integer, String, Boolean, Text, ForeignKey, TIMESTAMP
from sqlalchemy.sql import func
from database.database import Base


class User(Base):
    __tablename__ = "add_user"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    role = Column(String(50), nullable=False)  # user, employer, admin
    status = Column(String(20), default="Active")
    created_at = Column(TIMESTAMP, server_default=func.now())


class Announcement(Base):
    __tablename__ = "announcements"

    id = Column(Integer, primary_key=True)
    message = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("add_user.id"))
    announcement_id = Column(Integer, ForeignKey("announcements.id"))
    is_read = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, server_default=func.now())


class SystemConfiguration(Base):
    __tablename__ = "system_configuration"

    id = Column(Integer, primary_key=True)
    max_job_postings = Column(Integer, default=100)
    enable_user_registration = Column(Boolean, default=True)
    require_admin_approval = Column(Boolean, default=True)
    email_notifications = Column(Boolean, default=True)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())