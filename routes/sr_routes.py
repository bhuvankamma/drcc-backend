from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from database.sr_database import get_connection
from config.sr_config import settings
from schemas.sr_schemas import RecruiterInvite

import smtplib
import ssl
import uuid
from email.message import EmailMessage

router = APIRouter()


# ---------------- EMAIL FUNCTION ----------------

def send_invite_email(name: str, email: str, company_name: str, link: str):
    print("EMAIL:", settings.SENDER_EMAIL)
    print("PASSWORD:", settings.SENDER_PASSWORD)
    html_content = f"""
    <h2>Hello {name},</h2>
    <p>You have been invited to join <strong>{company_name}</strong> Employer Portal.</p>
    <p>Click below to register:</p>
    <a href="{link}">{link}</a>
    """

    msg = EmailMessage()
    msg["From"] = settings.SENDER_EMAIL
    msg["To"] = email
    msg["Subject"] = f"Invitation to Join {company_name} Employer Portal"
    msg.add_alternative(html_content, subtype="html")

    context = ssl.create_default_context()

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls(context=context)
        server.login(settings.SENDER_EMAIL, settings.SENDER_PASSWORD)
        server.send_message(msg)


# ---------------- INVITE RECRUITER ----------------

@router.post("/invite")
def invite_recruiter(data: RecruiterInvite):

    token = str(uuid.uuid4())
    invite_link = f"http://localhost:8000/register/{token}"

    conn = get_connection()
    cursor = conn.cursor()

    # Check duplicate email
    cursor.execute("SELECT id FROM recruiters WHERE email = %s;", (data.email,))
    existing = cursor.fetchone()

    if existing:
        conn.close()
        raise HTTPException(status_code=400, detail="Email already invited")

    cursor.execute(
        """
        INSERT INTO recruiters (name, email, role, company_name, invite_token)
        VALUES (%s, %s, %s, %s, %s);
        """,
        (data.name, data.email, data.role, data.company_name, token)
    )

    conn.commit()
    conn.close()

    send_invite_email(data.name, data.email, data.company_name, invite_link)

    return JSONResponse({
        "message": "Invite email sent successfully",
        "invite_link": invite_link
    })


# ---------------- ADMIN VIEW INVITES ----------------

@router.get("/admin/invites")
def view_invites():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name, email, role, company_name, invite_token
        FROM recruiters
        ORDER BY id DESC;
    """)

    rows = cursor.fetchall()
    conn.close()

    invites = [
        {
            "id": row[0],
            "name": row[1],
            "email": row[2],
            "role": row[3],
            "company_name": row[4],
            "status": "Pending" if row[5] else "Registered"
        }
        for row in rows
    ]

    return {"invites": invites}

@router.get("/")
def root():
    return {"message": "API is running"}