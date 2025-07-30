from __future__ import annotations

from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, Annotated, Any, AsyncGenerator, Optional

from fastapi import Depends, FastAPI

from fastapi_mvp.metrics import MetricsSettings, instrument_app
from fastapi_mvp.settings.app_settings import AppSettings
from fastapi_mvp.storage.mongo_storage import (
    MongoSettings,
    MongoStorage,
    get_mongo_storage,
)
from fastapi_mvp.storage.s3_storage import (
    S3Settings,
    S3Storage,
    get_s3_storage,
)

if TYPE_CHECKING:
    from fastapi_mvp.settings.env_settings import LoadEnvSettings


@asynccontextmanager
async def lifespan(app: FastAPIMvp) -> AsyncGenerator[None, None]:
    await app.initialize()
    yield


def merge_lifespans(provided_lifespan: Optional[Any]) -> Any:
    if provided_lifespan is not None:
        err = "Providing custom lifespan is not supported yet"
        raise RuntimeError(err)

    return lifespan


class FastAPIMvp(FastAPI):
    __instance__: Optional[FastAPIMvp] = None
    __env_ready__: bool = False

    def __init__(
        self,
        mongo: Optional[MongoSettings] = None,
        s3: Optional[S3Settings] = None,
        metrics: Optional[MetricsSettings] = None,
        **kwargs: Any,
    ) -> None:
        if FastAPIMvp.__instance__ is not None:
            err = "You can not create several FastAPIMvp instances, it is singleton"
            raise RuntimeError(err)

        FastAPIMvp.prepare_env()
        merged = merge_lifespans(kwargs.pop("lifespan", None))
        super().__init__(**kwargs, lifespan=merged)

        if metrics:
            instrument_app(self, metrics)

        self.__mongo_settings = mongo
        self.__s3_settings = s3

        self.__mongo_storage: Optional[MongoStorage] = None
        self.__s3_storage: Optional[S3Storage] = None

        FastAPIMvp.__instance__ = self

    def mongo(self) -> MongoStorage:
        if self.__mongo_storage is None:
            err = "Provide mongo settings in constructor to use MongoDB."
            raise RuntimeError(err)

        return self.__mongo_storage

    def s3(self) -> S3Storage:
        if self.__s3_storage is None:
            err = "Provide s3 settings in constructor to use S3 Object Storage."
            raise RuntimeError(err)

        return self.__s3_storage

    async def initialize(self) -> None:
        if self.__mongo_settings:
            self.__mongo_storage = get_mongo_storage(self.__mongo_settings)
        if self.__s3_settings:
            self.__s3_storage = get_s3_storage(self.__s3_settings)

    @classmethod
    def prepare_env(cls, env: Optional[LoadEnvSettings] = None) -> None:
        if cls.__env_ready__ is True:
            return
        if env is not None:
            env.load()
        AppSettings.load_and_validate()
        cls.__env_ready__ = True

    @classmethod
    def instance(cls) -> FastAPIMvp:
        if cls.__instance__ is None:
            err = (
                "FastAPIMvp is not initialized, consider "
                "creating an instance before calling this method"
            )
            raise RuntimeError(err)
        return cls.__instance__


def get_mongo() -> MongoStorage:
    return FastAPIMvp.instance().mongo()


def get_s3() -> S3Storage:
    return FastAPIMvp.instance().s3()


MongoDep = Annotated[MongoStorage, Depends(get_mongo)]
S3Dep = Annotated[S3Storage, Depends(get_s3)]
