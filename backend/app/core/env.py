"""
Environment Variables Management

Loads environment variables from .env file in the project root.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional

# Get the project root directory (two levels up from this file)
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
ENV_FILE = PROJECT_ROOT / ".env"

# Load environment variables from .env file
load_dotenv(ENV_FILE)

def get_env(key: str, default: Optional[str] = None) -> Optional[str]:
    """Get environment variable with optional default value."""
    return os.getenv(key, default)

def get_required_env(key: str) -> str:
    """Get required environment variable, raise error if not found."""
    value = os.getenv(key)
    if value is None:
        raise ValueError(f"Required environment variable {key} is not set")
    return value

def get_bool_env(key: str, default: bool = False) -> bool:
    """Get boolean environment variable."""
    value = os.getenv(key, "").lower()
    return value in ("true", "1", "yes", "on")

def get_int_env(key: str, default: int = 0) -> int:
    """Get integer environment variable."""
    try:
        return int(os.getenv(key, str(default)))
    except ValueError:
        return default

# Application settings
APP_NAME = get_env("APP_NAME", "necessitas.ai")
APP_VERSION = get_env("APP_VERSION", "1.0.0")
DEBUG = get_bool_env("DEBUG", False)

# Database
DATABASE_URL = get_env("DATABASE_URL", "postgresql://user:password@localhost/careercompass")
REDIS_URL = get_env("REDIS_URL", "redis://localhost:6379")

# AWS Configuration
AWS_REGION = get_env("AWS_REGION", "us-east-1")
AWS_ACCESS_KEY_ID = get_env("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = get_env("AWS_SECRET_ACCESS_KEY")
TEXTRACT_ACCESS_KEY_ID = get_env("TEXTRACT_AWS_ACCESS_KEY_ID")
TEXTRACT_SECRET_ACCESS_KEY = get_env("TEXTRACT_AWS_SECRET_ACCESS_KEY")

# Bedrock Configuration
BEDROCK_MODEL_ID = get_env("BEDROCK_MODEL_ID", "anthropic.claude-3-sonnet-20240229-v1:0")
BEDROCK_AGENT_ID = get_env("BEDROCK_AGENT_ID")

# API Keys
CRUNCHBASE_API_KEY = get_env("CRUNCHBASE_API_KEY")
LINKEDIN_API_KEY = get_env("LINKEDIN_API_KEY")
INDEED_API_KEY = get_env("INDEED_API_KEY")
OPENAI_API_KEY = get_env("OPENAI_API_KEY")

# Adzuna API (for job search)
ADZUNA_APP_ID = get_env("ADZUNA_APP_ID")
ADZUNA_APP_KEY = get_env("ADZUNA_APP_KEY")

# File Storage
UPLOAD_BUCKET = get_env("UPLOAD_BUCKET", "careercompass-uploads")
MAX_FILE_SIZE = get_int_env("MAX_FILE_SIZE", 10 * 1024 * 1024)  # 10MB

# ML Models
SPACY_MODEL = get_env("SPACY_MODEL", "en_core_web_sm")
EMBEDDING_MODEL = get_env("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

# Caching
CACHE_TTL = get_int_env("CACHE_TTL", 3600)  # 1 hour

def get_aws_credentials() -> dict:
    """Get AWS credentials for agentcore runtime."""
    credentials = {}
    if AWS_ACCESS_KEY_ID:
        credentials["aws_access_key_id"] = AWS_ACCESS_KEY_ID
    if AWS_SECRET_ACCESS_KEY:
        credentials["aws_secret_access_key"] = AWS_SECRET_ACCESS_KEY
    if AWS_REGION:
        credentials["region_name"] = AWS_REGION
    return credentials

def get_textract_credentials() -> dict:
    """Get AWS credentials for Textract."""
    credentials = {}
    if TEXTRACT_ACCESS_KEY_ID:
        credentials["aws_access_key_id"] = TEXTRACT_ACCESS_KEY_ID
    if TEXTRACT_SECRET_ACCESS_KEY:
        credentials["aws_secret_access_key"] = TEXTRACT_SECRET_ACCESS_KEY
    if AWS_REGION:
        credentials["region_name"] = AWS_REGION
    return credentials

def get_adzuna_credentials() -> dict:
    """Get Adzuna credentials."""
    credentials = {}
    if ADZUNA_APP_ID:
        credentials["adzuna_app_id"] = ADZUNA_APP_ID
    if ADZUNA_APP_KEY:
        credentials["adzuna_app_key"] = ADZUNA_APP_KEY
    return credentials

def validate_required_settings() -> list[str]:
    """Validate that required settings are present. Returns list of missing settings."""
    missing = []

    # Check for required AWS credentials
    if not AWS_ACCESS_KEY_ID:
        missing.append("AWS_ACCESS_KEY_ID")
    if not AWS_SECRET_ACCESS_KEY:
        missing.append("AWS_SECRET_ACCESS_KEY")

    # Check for required API keys
    if not ADZUNA_APP_ID:
        missing.append("ADZUNA_APP_ID")
    if not ADZUNA_APP_KEY:
        missing.append("ADZUNA_APP_KEY")

    return missing

def is_production() -> bool:
    """Check if running in production environment."""
    return get_env("ENVIRONMENT", "development").lower() == "production"

# Validate settings on import
missing_settings = validate_required_settings()
if missing_settings:
    print(f"⚠️  Warning: Missing required environment variables: {', '.join(missing_settings)}")
    print("   Some features may not work properly.")
    print("   Please check your .env file and ensure all required variables are set.")
