from pydantic import BaseModel


# Insert test user (only 5 columns)
class TestInsertSchema(BaseModel):

    email: str
    name: str
    password: str
    role: str
    phone_number: str


# Update profile schema
class ProfileUpdateSchema(BaseModel):

    address: str | None = None
    previous_ctc: str | None = None
    expected_ctc: str | None = None
    notice_period: str | None = None
    field_of_work: str | None = None
    education: str | None = None
    experience: str | None = None
    skills: str | None = None
