"""
Configuration settings for GeoMeasure Platform.
Uses Pydantic BaseSettings with environment variable support.
"""
from pathlib import Path
from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    """Application configuration settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    PROJECT_NAME: str = "GeoMeasure"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # Database
    DATABASE_URL: str = "sqlite:///./geomeasure.db"
    USE_POSTGIS: bool = False

    # Security & Uploads
    MAX_UPLOAD_SIZE_MB: int = 50
    ALLOWED_EXTENSIONS: List[str] = [".kml", ".zip"]
    ALLOWED_MIME_TYPES: List[str] = [
        "application/vnd.google-earth.kml+xml",
        "application/xml",
        "text/xml",
        "application/zip",
        "application/x-zip-compressed",
        "application/octet-stream"
    ]
    UPLOAD_DIR: Path = BASE_DIR / "uploads"
    TEMP_DIR: Path = BASE_DIR / "uploads" / "temp"

    # ZIP bomb protection limits
    MAX_UNCOMPRESSED_RATIO: int = 100  # Max compression ratio
    MAX_ZIP_ENTRIES: int = 200
    MAX_TOTAL_UNCOMPRESSED_SIZE_MB: int = 250

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000"
    ]


settings = Settings()
