from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    DB_URL: str = 'mysql+aiomysql://{YOUR_USERNAME}:{YOUR_PASSWORD}@{YOUR_HOST}:{YOUR_PORT}/{YOUR_DB}'

    model_config = SettingsConfigDict(env_file=".env")


@lru_cache()
def get_setting():
    return Settings()
