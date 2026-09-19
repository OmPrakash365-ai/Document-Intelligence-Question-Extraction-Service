"""Core application configuration and settings."""

from functools import lru_cache
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # Application
    APP_NAME: str = "Document Intelligence & Question Extraction Service"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "default-insecure-secret-key-change-in-production-1234567890"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Database (PostgreSQL)
    DATABASE_URL: str = "postgresql+psycopg://postgres:postgres@localhost:5432/document_intelligence"
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_ECHO: bool = False

    # Redis & Celery
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    CELERY_TASK_ALWAYS_EAGER: bool = False

    # Security & JWT
    JWT_SECRET_KEY: str = "default-jwt-secret-key-change-in-production-1234567890"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # File Storage
    STORAGE_BACKEND: str = "local"
    STORAGE_BASE_PATH: str = "./storage"
    MAX_UPLOAD_SIZE_MB: int = 25
    ALLOWED_EXTENSIONS: List[str] = Field(default=["pdf", "jpg", "jpeg", "png"])
    ALLOWED_CONTENT_TYPES: List[str] = Field(
        default=["application/pdf", "image/jpeg", "image/png"]
    )

    # Document & OCR Processing
    OCR_PROVIDER: str = "tesseract"
    OCR_LANGUAGE: str = "eng"
    OCR_DPI: int = 300
    ENABLE_DESKEW: bool = True
    ENABLE_DENOISE: bool = True

    # Confidence Thresholds
    HIGH_CONFIDENCE_THRESHOLD: float = 0.85
    MEDIUM_CONFIDENCE_THRESHOLD: float = 0.65

    # Optional External AI/Vision Provider
    AI_PROVIDER: str = "none"
    AI_API_KEY: Optional[str] = None
    AI_MODEL: Optional[str] = None


@lru_cache()
def get_settings() -> Settings:
    return Settings()
