from functools import lru_cache
from typing import Optional, Type

from pydantic import BaseModel

from fastapi_mvp.storage.mongo_storage.manager import MongoDBManager, get_manager
from fastapi_mvp.storage.mongo_storage.settings import MongoSettings


class MongoStorage:
    def __init__(self, manager: MongoDBManager) -> None:
        self.__manager = manager

    async def save[T: BaseModel](self, key: str, data: T) -> T:
        async with self.__manager as manager:
            await manager.save(key, data.model_dump_json())
        return data

    async def load[T: BaseModel](self, key: str, model_type: Type[T]) -> Optional[T]:
        async with self.__manager as manager:
            doc = await manager.load(key)
            return model_type.model_validate_json(doc) if doc else None


@lru_cache
def get_mongo_storage(settings: MongoSettings) -> MongoStorage:
    manager = get_manager(settings)
    return MongoStorage(manager)
