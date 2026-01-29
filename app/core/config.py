from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings"""

    # API Settings
    app_name: str = "Job Scraper API"
    version: str = "1.0.0"
    description: str = "FastAPI-based web scraping API for job listings"

    # Scraping Settings
    request_timeout: int = 30
    max_retries: int = 3
    user_agent_rotate: bool = True

    # Rate limiting
    requests_per_minute: int = 60

    # Environment
    debug: bool = False

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields in .env


# Global settings instance
settings = Settings()