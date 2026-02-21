from pydantic import BaseModel, EmailStr


class EmployerCreate(BaseModel):
    contact_person_name: str
    company_official_name: str
    email_address: EmailStr
    password: str
    confirm_password: str


class OTPVerify(BaseModel):
    email_address: EmailStr
    otp: str


class ForgotPasswordRequest(BaseModel):
    email_address: EmailStr


class ResetPassword(BaseModel):
    email_address: EmailStr
    otp: str
    new_password: str
    confirm_password: str
