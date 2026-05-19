from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Flowspace"
    APP_ENV: str = "development"
    SECRET_KEY: str = "changeme"

    # PostgreSQL
    DATABASE_URL: str = "postgresql+asyncpg://flowspace:flowspace@localhost:5432/flowspace"

    # MongoDB
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "flowspace"

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # AWS S3
    AWS_REGION: str = "ap-south-1"
    S3_BUCKET_NAME: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()