from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.db.database import get_db
from app.core.config import settings

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check():
    """Basic health check — confirms the API is running."""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "env": settings.APP_ENV,
    }


@router.get("/hello")
async def hello():
    """Simple hello endpoint."""
    return {"message": f"Welcome to {settings.APP_NAME}!"}


@router.post("/echo")
async def echo(body: dict):
    """Echoes back whatever JSON you send it. Good for testing."""
    return {"received": body}


@router.get("/health/db")
async def db_health_check(db: AsyncSession = Depends(get_db)):
    """Checks if the database connection is working."""
    await db.execute(text("SELECT 1"))
    return {"status": "database connected"}