from typing import Any
from pydantic import Field, ValidationInfo, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

INSECURE_DEV_SECRET_KEYS = {
    "default-secret-key-change-in-production-32bytes",
    "change-this-in-production-super-secret-key-32bytes",
    "dev-insecure-secret-key-do-not-use-in-prod-32b",
    "secret",
    "change-me",
}


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True, extra="ignore"
    )

    PROJECT_NAME: str = "AutoDS"
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    # API Configuration
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "dev-insecure-secret-key-do-not-use-in-prod-32b"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    # Database
    POSTGRES_USER: str = "autods_user"
    POSTGRES_PASSWORD: str = "autods_password"
    POSTGRES_DB: str = "autods_db"
    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: int = 5432
    DATABASE_URL: str | None = None

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: str | None, info: ValidationInfo) -> Any:
        if isinstance(v, str) and v:
            return v
        values = info.data
        user = values.get("POSTGRES_USER")
        password = values.get("POSTGRES_PASSWORD")
        host = values.get("POSTGRES_HOST")
        port = values.get("POSTGRES_PORT")
        db = values.get("POSTGRES_DB")
        return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{db}"

    # Redis & Celery
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_URL: str = "redis://redis:6379/0"

    # AI & OpenAI
    OPENAI_API_KEY: str | None = None

    # Storage
    STORAGE_BACKEND: str = "local"
    STORAGE_LOCAL_DIR: str = "./storage"

    @model_validator(mode="after")
    def validate_production_security(self) -> "Settings":
        is_production = self.ENVIRONMENT.lower() in ("production", "prod", "staging")
        if is_production:
            if not self.SECRET_KEY or self.SECRET_KEY in INSECURE_DEV_SECRET_KEYS:
                raise ValueError(
                    "CRITICAL SECURITY CONFIGURATION ERROR: SECRET_KEY must be set to a secure, unique string in production environments."
                )
            if len(self.SECRET_KEY) < 32:
                raise ValueError(
                    "CRITICAL SECURITY CONFIGURATION ERROR: SECRET_KEY must be at least 32 characters in length for production environments."
                )
        return self


settings = Settings()

