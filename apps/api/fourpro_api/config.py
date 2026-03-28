from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    environment: str = Field(default="development", alias="ENVIRONMENT")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    database_url: str = Field(..., alias="DATABASE_URL")

    jwt_secret: str = Field(..., alias="JWT_SECRET")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default=15, alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(default=7, alias="REFRESH_TOKEN_EXPIRE_DAYS")

    login_rate_limit: str = Field(default="10/minute", alias="LOGIN_RATE_LIMIT")

    redis_url: str | None = Field(default=None, alias="REDIS_URL")
    upload_dir: str = Field(default="/data/uploads", alias="UPLOAD_DIR")
    max_upload_mb: int = Field(default=50, alias="MAX_UPLOAD_MB")

    # Lista separada por vírgulas ou "*" (dev). Com credentials JWT, prefira origens explícitas.
    cors_origins: str = Field(
        default="http://localhost:4200,http://127.0.0.1:4200,http://localhost:8081,http://127.0.0.1:8081",
        alias="CORS_ORIGINS",
    )

    smtp_host: str | None = Field(default=None, alias="SMTP_HOST")
    smtp_port: int = Field(default=587, alias="SMTP_PORT")
    smtp_user: str | None = Field(default=None, alias="SMTP_USER")
    smtp_password: str | None = Field(default=None, alias="SMTP_PASSWORD")
    smtp_from: str = Field(default="no-reply@4pro-bi.local", alias="SMTP_FROM")
    smtp_use_tls: bool = Field(default=True, alias="SMTP_USE_TLS")

    app_public_url: str = Field(
        default="http://localhost:8081",
        alias="APP_PUBLIC_URL",
        description="Base URL do front (links em emails de reset).",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


def reset_settings_cache() -> None:
    """Para testes que alteram variáveis de ambiente."""
    get_settings.cache_clear()
