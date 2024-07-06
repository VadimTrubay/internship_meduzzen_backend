from dotenv import load_dotenv

from pydantic.v1 import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    APP_HOST: str
    APP_PORT: int
    DEBUG: bool

    DB_USER: str
    DB_NAME: str
    DB_HOST: str
    DB_PORT: int
    DB_PASSWORD: str

    REDIS_PORT: int
    REDIS_HOST: str

    class Config:
        env_file = ".env"


settings = Settings()
