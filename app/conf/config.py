from dotenv import load_dotenv

from pydantic.v1 import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    APP_HOST: str
    APP_PORT: int
    DEBUG: bool

    class Config:
        env_file = ".env"


settings = Settings()
