import os
import json
import random
import time

otp_store = {}

def handler(request, context):
    data = json.loads(request.body)
    email = data.get("email")
    if not email:
        return {"statusCode": 400, "body": json.dumps({"error": "Email is required"})}

    # Generate OTP
    otp = ''.join([str(random.randint(0,9)) for _ in range(6)])
    expiry_time = time.time() + 5*60  # 5 minutes
    otp_store[email] = {"otp": otp, "expiry": expiry_time}

    # For now, just return OTP (do NOT send email yet)
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"email": email, "otp": otp, "expiry": expiry_time})
    }
