from pydantic import BaseModel
from typing import Optional

# Insert test user (only 5 columns)
class TestInsertSchema(BaseModel):
    email: str
    name: str
    password: str
    role: str
    phone_number: str

# Update profile schema
# Using Optional (| None = None) so updates don't require every single field
class ProfileUpdateSchema(BaseModel):
    address: Optional[str] = None
    previous_ctc: Optional[str] = None
    expected_ctc: Optional[str] = None
    notice_period: Optional[str] = None
    field_of_work: Optional[str] = None
    education: Optional[str] = None
    experience: Optional[str] = None
    skills: Optional[str] = None