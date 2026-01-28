import os
from functools import lru_cache
from typing import Optional

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB_NAME = os.getenv("MONGO_DB", "solar_monitoring")


class MongoConnectionManager:
    """Singleton-style manager for MongoDB connections."""

    def __init__(self):
        self._client: Optional[AsyncIOMotorClient] = None

    def get_client(self) -> AsyncIOMotorClient:
        if not MONGO_URI:
            raise RuntimeError("MONGO_URI environment variable is not set")

        if self._client is None:
            self._client = AsyncIOMotorClient(MONGO_URI)
        return self._client

    def get_database(self) -> AsyncIOMotorDatabase:
        client = self.get_client()
        return client[MONGO_DB_NAME]

    async def close(self):
        if self._client is not None:
            self._client.close()
            self._client = None


@lru_cache
def get_connection_manager() -> MongoConnectionManager:
    return MongoConnectionManager()


def get_database() -> AsyncIOMotorDatabase:
    return get_connection_manager().get_database()


