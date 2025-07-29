import os
from dotenv import load_dotenv

# ✅ Load .env at import time
load_dotenv()

def get_secret(key: str, default=None, required=False):
    """
    Load secrets in the following priority:
    1. .env file
    2. System environment variable
    3. Default fallback (if provided)
    """
    value = os.getenv(key, default)

    if required and value is None:
        raise ValueError(f"Missing required secret: {key}")

    return value

def get_smtp_config():
    """
    Load SMTP config from environment variables.
    Supports both .env and direct env injection.
    """
    return {
        "host": get_secret("SMTP_HOST", required=True),
        "port": int(get_secret("SMTP_PORT", 587)),
        "username": get_secret("SMTP_USERNAME", required=True),
        "password": get_secret("SMTP_PASSWORD", required=True),
        "use_tls": get_secret("SMTP_USE_TLS", "true").lower() == "true",
        "rate_limit": int(get_secret("SMTP_RATE_LIMIT", 20))
    }
