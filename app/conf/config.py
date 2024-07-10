from dotenv import find_dotenv

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=find_dotenv(filename=".env", usecwd=True),
        env_file_encoding="utf-8",
        extra="allow",
    )
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

    AUTH0_SECRET: str
    AUTH0_DOMAIN: str
    AUTH0_API_AUDIENCE: str
    AUTH0_ALGORITHMS: str
    AUTH0_USERNAME_PREFIX: str
    CLIENT_URI: str
    ISSUER: str
    TOKEN_EXPIRATION: int


settings = Settings()
