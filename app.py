import os
from dotenv import load_dotenv
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
import logging
from functools import wraps
import requests 
import json

# --- PostgreSQL Imports ---
import psycopg2
from psycopg2 import extras
from psycopg2 import errors as pg_errors 

# ---------------------- Load Environment Variables ----------------------
load_dotenv()

# ---------------------- Logging ----------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------------- Flask ----------------------
app = Flask(__name__)
ALLOWED_ORIGINS = os.environ.get("ALLOWED_ORIGINS", "https://www.yuvasaathi.in").split(',')
CORS(app, resources={r"/*": {"origins": ALLOWED_ORIGINS, "supports_credentials": True}}) 

# ---------------------- Environment Variables ----------------------
SENDER_EMAIL = os.environ.get("SENDER_EMAIL")
SENDER_PASSWORD = os.environ.get("SENDER_PASSWORD")
OTP_EXPIRY = 300 # 5 minutes

AWS_REGISTER_URL = os.environ.get(
    "AWS_REGISTER_URL", 
    "https://yc7uonaqnl.execute-api.eu-north-1.amazonaws.com/prod/register"
)

# ⭐ PostgreSQL RDS Credentials 
DB_HOST = os.environ.get("DB_HOST")
DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS") 
DB_PORT = os.environ.get("DB_PORT", "5432")

# ⭐ Skills API Configuration 
APILAYER_SKILLS_API_KEY = os.environ.get("APILAYER_SKILLS_API_KEY") 
APILAYER_SKILLS_BASE_URL = "https://api.apilayer.com/skills"
SKILL_QUERIES = [
    ("Full Stack Development", "IT"),
    ("Data Science and AI", "IT"),
    ("Digital Marketing Strategy", "NON-IT"),
    ("Financial Accounting Tally", "NON-IT"),
    ("Cloud DevOps Engineering", "IT"),
    ("Creative Graphic Design", "NON-IT"),
]
MAX_SKILLS_PER_QUERY = 25 

# ---------------------- PostgreSQL Connection ----------------------
db_conn = None

def get_db_connection():
    """Initializes or returns a persistent PostgreSQL database connection."""
    global db_conn
    if db_conn is None or db_conn.closed != 0:
        logger.info("INFO: Initializing new PostgreSQL connection.")
        if not all([DB_HOST, DB_NAME, DB_USER, DB_PASS]):
            logger.error("❌ PostgreSQL environment variables are missing.")
            return None
        try:
            db_conn = psycopg2.connect(
                host=DB_HOST,
                database=DB_NAME,
                user=DB_USER,
                password=DB_PASS,
                port=DB_PORT,
                connect_timeout=5
            )
        except Exception as e:
            logger.error(f"❌ FAILED TO CONNECT TO POSTGRESQL: {e}")
            return None
    return db_conn
    
get_db_connection()

# ---------------------- Helper Functions ----------------------
def handle_exceptions(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            logger.exception("Unhandled exception")
            return jsonify({"error": "An internal server error occurred."}), 500
    return wrapper

def send_otp_email(to_email, otp):
    try:
        msg = MIMEMultipart()
        msg["From"] = SENDER_EMAIL
        msg["To"] = to_email
        msg["Subject"] = "Your OTP for YuvaSaathi"
        msg.attach(MIMEText(f"Your OTP is: {otp}\nValid for 5 minutes", "plain"))
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, to_email, msg.as_string())
        logger.info(f"✅ OTP sent to {to_email}")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to send OTP email: {e}")
        return False

# ---------------------- Core Authentication Logic ----------------------
def _generate_otp_logic(connection, identifier):
    if not identifier:
        return jsonify({"error": "Identifier (email/mobile) is required."}), 400
    otp = str(random.randint(100000, 999999))
    sql_upsert = """
    INSERT INTO otp_codes (user_email_ref, code, created_at, expires_at, recipient_identifier)
    VALUES (%s, %s, NOW(), NOW() + interval '5 minutes', %s)
    ON CONFLICT (user_email_ref) DO UPDATE 
    SET 
        code = EXCLUDED.code, 
        created_at = NOW(), 
        expires_at = NOW() + interval '5 minutes',
        recipient_identifier = EXCLUDED.recipient_identifier;
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql_upsert, (identifier, otp, identifier))
            connection.commit()
        if '@' in identifier and send_otp_email(identifier, otp):
            return jsonify({"message": f"OTP sent successfully to {identifier}."}), 200
        else:
            connection.rollback()
            return jsonify({"error": "Failed to send OTP. Please check the identifier."}), 500
    except Exception as e:
        connection.rollback()
        logger.error(f"❌ PostgreSQL OTP GENERATION failed: {e}")
        return jsonify({"error": "An internal server error occurred during OTP generation."}), 500

def _verify_login_logic(connection, identifier, otp_code):
    if not all([identifier, otp_code]):
        return jsonify({"error": "Identifier and OTP are required"}), 400
    sql_check = "SELECT code, expires_at FROM otp_codes WHERE user_email_ref = %s;"
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql_check, (identifier,))
            record = cursor.fetchone()
            if not record:
                return jsonify({"error": "OTP not found for this identifier. Please generate a new one."}), 404
            stored_otp, expires_at = record
            if expires_at < psycopg2.Timestamp(time.time()): 
                return jsonify({"error": "OTP expired. Please regenerate."}), 401
            if stored_otp != otp_code:
                return jsonify({"error": "Invalid OTP."}), 401
            sql_delete = "DELETE FROM otp_codes WHERE user_email_ref = %s;"
            cursor.execute(sql_delete, (identifier,))
            connection.commit()
            return jsonify({"message": "Login successful. Token placeholder."}), 200
    except Exception as e:
        connection.rollback()
        logger.error(f"❌ PostgreSQL LOGIN VERIFICATION failed: {e}")
        return jsonify({"error": "An internal server error occurred during login."}), 500

# -------------------------------------------------------------------------
# ⭐ UNIFIED API ENDPOINT: /api/auth
# -------------------------------------------------------------------------
@app.route("/api/auth", methods=["POST", "OPTIONS"])
@handle_exceptions
def handle_auth():
    if request.method == "OPTIONS":
        return jsonify({}), 200
    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "Authentication service is temporarily unavailable."}), 503
    data = request.get_json(silent=True)
    if not data or 'action' not in data or 'identifier' not in data:
        return jsonify({"error": "Invalid request payload. 'action' and 'identifier' are required."}), 400
    action = data.get("action").upper()
    identifier = data.get("identifier").strip()
    logger.info(f"[AUTH] action={action}, identifier={identifier}")
    if action == "GENERATE_OTP":
        return _generate_otp_logic(connection, identifier)
    elif action == "VERIFY_LOGIN":
        otp_code = data.get("otp_code")
        return _verify_login_logic(connection, identifier, otp_code)
    else:
        return jsonify({"error": "Invalid action specified."}), 400

# --------------------------------------------------------------------------------------
# ⭐ Skills Proxy Route
# --------------------------------------------------------------------------------------
@app.route("/api/skills-proxy", methods=["GET", "OPTIONS"])
@handle_exceptions
def get_skills_proxy():
    if request.method == "OPTIONS":
        return jsonify({}), 200
    if not APILAYER_SKILLS_API_KEY:
        return jsonify({"error": "Skills service is unavailable. API Key not configured."}), 503
    all_skills = []
    for query_text, category in SKILL_QUERIES:
        headers = {"apikey": APILAYER_SKILLS_API_KEY}
        params = {"q": query_text, "count": MAX_SKILLS_PER_QUERY}
        try:
            api_response = requests.get(APILAYER_SKILLS_BASE_URL, headers=headers, params=params, timeout=10)
            api_response.raise_for_status()
            skill_list = api_response.json()
            for raw_skill_name in skill_list:
                if raw_skill_name.strip() not in [s['title'] for s in all_skills]:
                    skill_id = hash(raw_skill_name.strip()) % (10**6)
                    final_skill = {
                        "id": skill_id,
                        "title": raw_skill_name.strip(),
                        "category": category,
                        "description": f"Explore opportunities in {raw_skill_name.strip()} under the {category} sector.",
                        "certification": f"Bihar Govt. Certified {category} Program",
                        "image_url": f"/images/{category.lower()}_default.jpg",
                        "is_featured": (category == "IT" and len(all_skills) < 10)
                    }
                    all_skills.append(final_skill)
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Skills API Request Failed for '{query_text}': {e}")
    if not all_skills:
        return jsonify({"error": "Failed to fetch any skills from the external API."}), 503
    return jsonify(all_skills)

@app.route("/api/test-db")
def test_db():
    connection = get_db_connection()
    if not connection:
        return jsonify({"status": "error", "message": "PostgreSQL connection failed."}), 500
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1;")
        return jsonify({"status": "ok", "message": "PostgreSQL connection successful"})
    except Exception as e:
        return jsonify({"status": "error", "message": f"PostgreSQL test query failed: {str(e)}"}), 500

# --------------------------------------------------------------------------------------
# ⭐ FIXED /api/register Proxy Route
# --------------------------------------------------------------------------------------
@app.route("/api/register", methods=["POST", "OPTIONS"])
@handle_exceptions
def register_user_serverless():
    if request.method == "OPTIONS":
        return jsonify({}), 200
    if not AWS_REGISTER_URL:
        return jsonify({"error": "Registration service is unavailable."}), 503
    try:
        data = request.get_json(silent=True)
        if not data:
            try:
                data = request.data.decode('utf-8')
                data = json.loads(data)
            except Exception:
                return jsonify({"error": "Invalid or missing JSON payload in request."}), 400

        logger.info(f"[REGISTER] Sending request to Lambda with payload: {data}")
        aws_response = requests.post(AWS_REGISTER_URL, json=data, timeout=15)

        try:
            lambda_json = aws_response.json()
        except Exception:
            lambda_json = {"error": "Invalid response from Lambda", "raw_text": aws_response.text}

        logger.info(f"[REGISTER] Lambda response: status={aws_response.status_code}, body={lambda_json}")

        # Return Lambda status code and body so frontend sees duplicates/errors correctly
        return jsonify(lambda_json), aws_response.status_code

    except requests.exceptions.Timeout:
        return jsonify({"error": "Registration server timed out. Please try again."}), 504
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Registration proxy request failed: {e}")
        return jsonify({"error": "Failed to connect to the authentication server. Please try again."}), 503
    except Exception as e:
        logger.exception("Internal error during registration proxy.")
        return jsonify({"error": "An internal server error occurred during registration proxy."}), 500

# ---------------------- Main ----------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
