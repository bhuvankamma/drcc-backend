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

    address: str 
    previous_ctc: str 
    expected_ctc: str 
    notice_period: str
    field_of_work: str
    education: str 
    experience: str 
    skills: str
