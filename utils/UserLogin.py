"""
App and SMTP configuration.
"""
# SMTP (Gmail)
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "chandinisahasra02@gmail.com"
SMTP_PASSWORD = "tcyqwpvblcpuyhnd"

# OTP
OTP_EXPIRE_MINUTES = 5
OTP_LENGTH = 6

# JWT (change in production)
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours
