from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings


# The engine is the core connection to PostgreSQL
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.APP_ENV == "development",  # logs SQL in dev only
    pool_size=10,
    max_overflow=20,
)

# Session factory — creates new DB sessions on demand
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# Base class that all our database models will inherit from
class Base(DeclarativeBase):
    pass


# Dependency — FastAPI will call this to get a DB session per request
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()