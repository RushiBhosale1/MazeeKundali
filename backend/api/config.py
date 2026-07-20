"""
api/config.py
Application configuration via environment variables.
Uses pydantic-settings for type-safe config loading.
"""
from __future__ import annotations
from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # App
    app_env: str = "development"
    app_secret_key: str = "change-me-in-production"

    # Database
    database_url: str = "postgresql+asyncpg://kundali_user:kundali_pass@localhost:5432/kundali_db"
    database_url_sync: str = "postgresql://kundali_user:kundali_pass@localhost:5432/kundali_db"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Swiss Ephemeris
    ephe_path: str = "./static/ephemeris"

    # Geocoding
    geocoding_provider: str = "nominatim"
    nominatim_user_agent: str = "kundali-platform/1.0"

    # Cloudinary (PDF + image storage — replaces R2)
    cloudinary_cloud_name: Optional[str] = None
    cloudinary_api_key: Optional[str] = None
    cloudinary_api_secret: Optional[str] = None
    cloudinary_folder: str = "mazeekundali"     # folder prefix in Cloudinary

    # Razorpay
    razorpay_key_id: Optional[str] = None
    razorpay_key_secret: Optional[str] = None
    razorpay_webhook_secret: Optional[str] = None

    # Sentry
    sentry_dsn: Optional[str] = None
    
    # Resend
    resend_api_key: Optional[str] = None
    resend_from_email: str = "hello@mazeekundali.in"

    # Rate Limiting
    rate_limit_geocode: str = "30/minute"
    rate_limit_kundali_create: str = "5/10minutes"

    # Admin Dashboard
    admin_token: Optional[str] = None

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @property
    def is_development(self) -> bool:
        return self.app_env == "development"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()
