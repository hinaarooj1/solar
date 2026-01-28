from typing import Any, Dict, Optional

from motor.motor_asyncio import AsyncIOMotorCollection, AsyncIOMotorDatabase


class UserRepository:
    """Wrapper around the users collection for common operations."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection: AsyncIOMotorCollection = db["users"]

    async def get_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        return await self.collection.find_one({"username": username})

    async def get_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        return await self.collection.find_one({"_id": user_id})

    async def get_all_active_users(self) -> list[Dict[str, Any]]:
        cursor = self.collection.find({"is_active": {"$ne": False}})
        return await cursor.to_list(length=None)

    async def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        if "_id" not in user_data:
            user_data["_id"] = user_data["username"]
        await self.collection.insert_one(user_data)
        return user_data

    async def update_notification_email(self, user_id: str, email: Optional[str]) -> None:
        await self.update_user(
            user_id,
            {
                "notification_email": email,
                "updated_at": user_data_timestamp(),
            },
        )

    async def update_user(self, user_id: str, updates: Dict[str, Any]) -> None:
        updates = {**updates, "updated_at": user_data_timestamp()}
        await self.collection.update_one({"_id": user_id}, {"$set": updates})

    async def list_users(self) -> list[Dict[str, Any]]:
        cursor = self.collection.find(
            {},
            {
                "_id": 0,
                "username": 1,
                "notification_email": 1,
                "is_active": 1,
                "created_at": 1,
            },
        )
        return await cursor.to_list(length=None)


def user_data_timestamp():
    from datetime import datetime

    return datetime.utcnow().isoformat()

