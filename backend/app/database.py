from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from app.config import settings
from app.models import User, Question, Progress

_client: AsyncIOMotorClient | None = None


async def init_db():
    global _client
    _client = AsyncIOMotorClient(settings.mongo_uri)
    db = _client[settings.mongo_db_name]
    await init_beanie(database=db, document_models=[User, Question, Progress])
    return db
