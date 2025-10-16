"""
necessitas.ai Configuration

Centralized configuration management for the application.
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings."""

    # Application
    app_name: str = "necessitas.ai"
    app_version: str = "1.0.0"
    debug: bool = False

    # Database
    database_url: str = "postgresql://user:password@localhost/careercompass"
    redis_url: str = "redis://localhost:6379"

    # AWS
    aws_region: str = "us-east-1"
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None

    # Bedrock
    bedrock_model_id: str = "anthropic.claude-3-sonnet-20240229-v1:0"
    bedrock_agent_id: Optional[str] = None

    # API Keys
    crunchbase_api_key: Optional[str] = None
    linkedin_api_key: Optional[str] = None
    indeed_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None

    # File Storage
    upload_bucket: str = "careercompass-uploads"
    max_file_size: int = 10 * 1024 * 1024  # 10MB

    # ML Models
    spacy_model: str = "en_core_web_sm"
    embedding_model: str = "all-MiniLM-L6-v2"

    # Caching
    cache_ttl: int = 3600  # 1 hour

    class Config:
        env_file = ".env"
        case_sensitive = False

    # Adzuna API credentials
    adzuna_app_id: str = "14d37c2b"
    adzuna_app_key: str = "a79b17f868b53ee23f5ef701db02a24e"

# Global settings instance
settings = Settings()
