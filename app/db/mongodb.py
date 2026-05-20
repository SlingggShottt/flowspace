from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

client: AsyncIOMotorClient = None


async def get_mongodb():
    return client[settings.MONGODB_DB_NAME]


async def connect_mongodb():
    global client
    client = AsyncIOMotorClient(settings.MONGODB_URL)


async def close_mongodb():
    global client
    if client:
        client.close()