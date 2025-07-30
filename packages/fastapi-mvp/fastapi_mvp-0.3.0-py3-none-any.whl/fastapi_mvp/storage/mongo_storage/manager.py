from __future__ import annotations

from functools import lru_cache
from typing import TYPE_CHECKING, Optional

from motor.motor_asyncio import (
    AsyncIOMotorClient,
    AsyncIOMotorCollection,
    AsyncIOMotorDatabase,
)

if TYPE_CHECKING:
    from fastapi_mvp.storage.mongo_storage.settings import MongoSettings


DocumentType = dict[str, str]
CollectionType = AsyncIOMotorCollection[DocumentType]
DatabaseType = AsyncIOMotorDatabase[DocumentType]
MotorClientType = AsyncIOMotorClient[DocumentType]


class MongoDBManager:
    def __init__(self, settings: MongoSettings) -> None:
        self.settings = settings
        self.client: Optional[MotorClientType] = None
        self.db: Optional[DatabaseType] = None
        self.collection: Optional[CollectionType] = None

    async def __aenter__(self) -> MongoDBManager:
        self.client = AsyncIOMotorClient(self.settings.url())
        self.db = self.client[self.settings.name]
        self.collection = self.db["data"]
        return self

    async def __aexit__(self, _, __, ___) -> None:  # type: ignore
        if self.client:
            self.client.close()

    async def save(self, key: str, value: str) -> str:
        await self.ready_collection().update_one(
            {"_id": key},
            {"$set": {"data": value}},
            upsert=True,
        )
        return value

    async def load(self, key: str) -> Optional[str]:
        doc = await self.ready_collection().find_one({"_id": key})
        return doc.get("data") if doc else None

    def ready_collection(self) -> CollectionType:
        if self.collection is None:
            err = "Mongo manager is not ready: self.collection is None"
            raise RuntimeError(err)

        return self.collection


@lru_cache
def get_manager(settings: MongoSettings) -> MongoDBManager:
    return MongoDBManager(settings)
