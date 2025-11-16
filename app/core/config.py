import os  # noqa: F401
from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings


# Loading environment variables from .env
load_dotenv()


class Settings(BaseSettings):
    # App settings
    APP_NAME: str = "Africa Soko Backend"
    APP_ENV: str = "development"
    DEBUG: bool = True
    APP_PORT: int = 8000

    # JWT settings
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # Database settings
    POSTGRES_USER: str = Field(..., env="POSTGRES_USER")
    POSTGRES_PASSWORD: str = Field(..., env="POSTGRES_PASSWORD")
    POSTGRES_DB: str = Field(..., env="POSTGRES_DB")
    POSTGRES_HOST: str = Field(..., env="POSTGRES_HOST")
    POSTGRES_PORT: int = Field(..., env="POSTGRES_PORT")
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    GOOGLE_USER_DEFAULT_PASSWORD: str = Field(..., env="GOOGLE_USER_DEFAULT_PASSWORD")

    @property
    def SQLALCHEMY_DATABASE_URL(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:"
            f"{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:"
            f"{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


# Singleton settings object
settings = Settings()
