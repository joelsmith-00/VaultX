"""VaultX - Environment Configuration"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
from functools import lru_cache

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )
    ENVIRONMENT: str = "development"
    SECRET_KEY: str = "change-me-in-production"
    DEBUG: bool = True
    DATABASE_URL: str = "postgresql+asyncpg://vaultx:vaultx@localhost:5432/vaultx"
    REDIS_URL: str = "redis://localhost:6379/0"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    S3_ENDPOINT_URL: str = "http://localhost:9000"
    S3_ACCESS_KEY: str = "minioadmin"
    S3_SECRET_KEY: str = "minioadmin"
    S3_BUCKET_NAME: str = "vaultx"
    S3_REGION: str = "us-east-1"
    MAX_UPLOAD_SIZE_BYTES: int = 524288000
    ALLOWED_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    FRONTEND_URL: str = "http://localhost:5173"

@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
