import os.path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=f'{os.path.dirname(__file__)}/../../.env', extra='ignore')

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
    DB_URI: str = "sqlite+aiosqlite:///./database.sqlite"

    API_SCHEME: str = "http"
    API_URL: str = "127.0.0.1:8000"
    QR_CODE_ENDPOINT: str = "/qr_code/{uuid}"

    CORS_ORIGINS: list[str] = []
    COOKIE_SECURE: bool = False
    COOKIE_SAMESITE: Literal["lax", "strict", "none"] = "lax"

    ADMIN_USERNAME: str | None = None
    ADMIN_PASSWORD: str | None = None

    BOT_SHARED_SECRET: str | None = None
    BOT_TOKEN: str | None = None
    BOT_USERNAME: str | None = None

    GOOGLE_CLIENT_ID: str | None = None
    GOOGLE_CLIENT_SECRET: str | None = None


settings = Settings()  # type: ignore[call-arg]  # required fields come from .env / environment
