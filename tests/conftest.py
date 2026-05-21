import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from unittest.mock import patch, AsyncMock
from app.main import app
from app.db.database import get_db, Base

TEST_DATABASE_URL = "postgresql+asyncpg://flowspace:flowspace@localhost:5432/flowspace_test"


@pytest_asyncio.fixture(scope="function")
async def db_engine():
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        connect_args={"ssl": False},
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def client(db_engine):
    session_factory = async_sessionmaker(
        db_engine, class_=AsyncSession, expire_on_commit=False
    )

    async def override_get_db():
        async with session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    app.dependency_overrides[get_db] = override_get_db

    with patch("app.db.mongodb.connect_mongodb", new_callable=AsyncMock), \
         patch("app.db.mongodb.close_mongodb"), \
         patch("app.db.mongodb.get_mongodb", new_callable=AsyncMock) as mock_mongo:

        mock_db = AsyncMock()
        mock_db.comments.insert_one = AsyncMock(return_value=AsyncMock(inserted_id="test_id"))
        mock_db.comments.find = AsyncMock(return_value=AsyncMock(__aiter__=AsyncMock(return_value=iter([]))))
        mock_db.activities.insert_one = AsyncMock()
        mock_db.activities.find = AsyncMock(return_value=AsyncMock(__aiter__=AsyncMock(return_value=iter([]))))
        mock_mongo.return_value = mock_db

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as ac:
            yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def registered_user(client):
    response = await client.post("/auth/register", json={
        "company_name": "Test Company",
        "email": "test@example.com",
        "password": "password123",
        "name": "Test User",
    })
    return response.json()


@pytest_asyncio.fixture
async def auth_headers(registered_user):
    token = registered_user["access_token"]
    return {"Authorization": f"Bearer {token}"}