from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    BOT_TOKEN: str
    BOT_SHARED_SECRET: str
    BACKEND_URL: str = "http://backend:8000"
    SESSION_DB_PATH: str = "/data/bot_sessions.sqlite"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
