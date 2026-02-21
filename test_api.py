import requests

BASE_URL = "https://yuvasaathi-backend-v2.vercel.app"
test_email = "bhuvankalyankumar2000@gmail.com"
url = f"{BASE_URL}/api/generate-otp"
payload = {"email": test_email}

try:
    response = requests.post(url, json=payload, timeout=10)
    print("Status Code:", response.status_code)
    try:
        print("Response JSON:", response.json())
    except Exception as e:
        print("❌ JSON parsing error:", e)
        print("Raw response text:", response.text)
except Exception as e:
    print("❌ Error making request:", e)
