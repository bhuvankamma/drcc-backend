# routers/auth.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from database.database import get_connection

router = APIRouter(tags=["Auth"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ----------- Request Model -----------
class LoginRequest(BaseModel):
    official_email: EmailStr
    password: str


# ----------- Login API -----------
@router.post("/login")
def login_user(data: LoginRequest):

    conn = get_connection()
    cursor = conn.cursor()

    try:
        query = """
        SELECT id, full_name, password 
        FROM admins44 
        WHERE official_email = %s
        """

        cursor.execute(query, (data.official_email,))
        user = cursor.fetchone()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        user_id, full_name, stored_hash = user

        # 🔐 Verify password
        if not pwd_context.verify(data.password, stored_hash):
            raise HTTPException(status_code=401, detail="Invalid password")

        return {
            "message": "Login successful",
            "user_id": user_id,
            "full_name": full_name
        }

    finally:
        cursor.close()
        conn.close()