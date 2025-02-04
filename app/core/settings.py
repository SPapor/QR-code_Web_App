from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    db_name: str = 'database.sqlite'


settings = Settings(_env_file='../.env')
