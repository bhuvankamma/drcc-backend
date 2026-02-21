import os
import random
import time
import smtplib
import re
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pymongo import MongoClient, ASCENDING

# ---------------------- Config ----------------------
SENDER_EMAIL = os.environ.get("SENDER_EMAIL", "bhuvankalyankumar2000@gmail.com")
SENDER_PASSWORD = os.environ.get("SENDER_PASSWORD")
MONGO_URI = os.environ.get("MONGO_URI") 
OTP_EXPIRY = 300  # seconds (5 minutes)

# ---------------------- MongoDB Setup ----------------------
if not MONGO_URI:
    # In Vercel, this exception will return a 500 error, which is better than a silent failure
    raise ValueError("MongoDB URI not set in environment variables")

client = MongoClient(MONGO_URI)
db = client.get_default_database()
otp_collection = db.get_collection("otp_collection")

# Ensure index on email for faster lookup and uniqueness
otp_collection.create_index([("email", ASCENDING)], unique=True, background=True) # Added background=True for production safety

# ---------------------- Helpers (UNCHANGED) ----------------------
def is_valid_email(email):
    # ... (unchanged) ...
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

def send_otp_email(to_email, otp):
    # ... (unchanged) ...
    try:
        msg = MIMEMultipart()
        msg["From"] = SENDER_EMAIL
        msg["To"] = to_email
        msg["Subject"] = "Your OTP for YuvaSaathi"
        msg.attach(MIMEText(
            f"Dear user,\n\nYour OTP is: {otp}\n\nThis OTP is valid for 5 minutes.\n\nRegards,\nYuvaSaathi Team",
            "plain"
        ))

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, to_email, msg.as_string())

        return True
    except smtplib.SMTPException as smtp_err:
        print(f"SMTP error: {smtp_err}")
        return False

# ---------------------- Handler (The Fix) ----------------------
def handler(request, context):
    
    # ⭐️ FIX: Define complete set of CORS headers once
    CORS_HEADERS = {
        "Access-Control-Allow-Origin": "https://www.yuvasaathi.in",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization", # Added Authorization just in case
        "Access-Control-Allow-Credentials": "true", # Important if cookies/auth are used
        "Access-Control-Max-Age": "86400" # Cache preflight response for 24 hours
    }

    # Handle CORS preflight
    if request.method == "OPTIONS":
        return {
            "statusCode": 200,
            "headers": CORS_HEADERS,
            "body": ""
        }

    # Use the complete headers for the main response
    headers = CORS_HEADERS

    try:
        # Assuming request.body is bytes, which is typical for Vercel/Lambda
        body_string = request.body.decode('utf-8')
        data = json.loads(body_string)
        to_email = data.get("email")

        if not to_email or not is_valid_email(to_email):
            return {
                "statusCode": 400,
                "headers": headers,
                "body": json.dumps({"error": "Valid email is required"})
            }

        if not SENDER_EMAIL or not SENDER_PASSWORD:
            return {
                "statusCode": 500,
                "headers": headers,
                "body": json.dumps({"error": "Email credentials not configured"})
            }

        # Generate OTP
        otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        timestamp = int(time.time())

        # Upsert OTP into MongoDB
        otp_collection.update_one(
            {"email": to_email},
            {"$set": {"otp": otp, "created_at": timestamp}},
            upsert=True
        )

        # Send OTP via email
        if not send_otp_email(to_email, otp):
            return {
                "statusCode": 500,
                "headers": headers,
                "body": json.dumps({"error": "Failed to send OTP email"})
            }

        return {
            "statusCode": 200,
            "headers": headers,
            "body": json.dumps({"message": "OTP sent successfully"})
        }

    except json.JSONDecodeError:
        return {
            "statusCode": 400,
            "headers": headers,
            "body": json.dumps({"error": "Invalid JSON payload"})
        }
    except Exception as e:
        print(f"Unhandled error: {e}")
        return {
            "statusCode": 500,
            "headers": headers,
            "body": json.dumps({"error": "Internal server error"})
        }