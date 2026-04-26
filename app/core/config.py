import os
from dotenv import load_dotenv

load_dotenv()

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./pulse.db")

# Auth
SECRET_KEY = os.getenv("SECRET_KEY", "change-this-in-production")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRY_HOURS = int(os.getenv("JWT_EXPIRY_HOURS", "24"))

# Monitoring
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "30"))
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "5"))

# HTTP headers for monitoring requests
DEFAULT_HEADERS = {
    "User-Agent": "Pulse-Monitor/2.0",
    "Accept": "*/*",
    "Connection": "keep-alive"
}