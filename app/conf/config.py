from functools import lru_cache
from pydantic.v1 import BaseSettings


class Settings(BaseSettings):
    APP_HOST: str
    APP_PORT: int

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()


settings = get_settings()

