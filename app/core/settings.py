from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='../.env')
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES:int = 1
    REFRESH_TOKEN_EXPIRE_MINUTES:int = 60 * 24 * 7
    db_name: str = 'database.sqlite'


settings = Settings()
