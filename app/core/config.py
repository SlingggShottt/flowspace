# app/core/config.py

from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env", case_sensitive=True)

    APP_NAME: str = "Flowspace"
    APP_ENV: str = "development"
    SECRET_KEY: str = "changeme"

    DATABASE_URL: str = "postgresql+asyncpg://flowspace:flowspace@localhost:5432/flowspace"

    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "flowspace"

    REDIS_URL: str = "redis://localhost:6379"

    AWS_REGION: str = "ap-south-1"
    S3_BUCKET_NAME: str = ""

    RAZORPAY_KEY_ID: str = ""
    RAZORPAY_KEY_SECRET: str = ""


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()