from __future__ import annotations

from pathlib import Path
from typing import Annotated, Optional

from dotenv import load_dotenv
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


class Mvp:
    __instance__: Optional[Mvp] = None

    def __init__(
        self,
        fastapi_app: FastAPI,
        mongo_storage: Optional[MongoStorage] = None,
        s3_storage: Optional[S3Storage] = None,
    ) -> None:
        self.__fastapi_app = fastapi_app  # pylint: disable=unused-private-member
        self.__mongo_storage = mongo_storage
        self.__s3_storage = s3_storage

    def mongo(self) -> MongoStorage:
        if self.__mongo_storage is None:
            err = "Provide mongo settings to Mvp.setup() to use MongoDB."
            raise RuntimeError(err)

        return self.__mongo_storage

    def s3(self) -> S3Storage:
        if self.__s3_storage is None:
            err = "Provide s3 settings to Mvp.setup() to use S3 Object Storage."
            raise RuntimeError(err)

        return self.__s3_storage

    @classmethod
    async def setup(
        cls,
        app: FastAPI,
        mongo: Optional[MongoSettings] = None,
        s3: Optional[S3Settings] = None,
        metrics: Optional[MetricsSettings] = None,
    ) -> None:
        AppSettings.load_and_validate()

        mongo_storage = get_mongo_storage(mongo) if mongo else None
        s3_storage = get_s3_storage(s3) if s3 else None

        if metrics:
            instrument_app(app, metrics)

        cls.__instance__ = cls(
            fastapi_app=app,
            mongo_storage=mongo_storage,
            s3_storage=s3_storage,
        )

    @staticmethod
    async def load_env(
        env: str,
        envs_dir: Optional[Path] = None,
        secrets: Optional[Path] = None,
    ) -> None:
        """
        Load environment variables from .env file.
        Secrets are read from another file if it exists.
        Values from secrets override values from .env file but not from the system.
        :param env: Current environment to be used as .env file name.
        :param envs_dir: Path to env files directory,
                         "envs" by default if none is specified.
        :param secrets: Path to env file with application secrets,
                        "envs/secrets.env" by default if none is specified.
        :return:
        """
        if envs_dir is None:
            envs_dir = Path("envs")
        if secrets is None:
            secrets = envs_dir / "secrets.env"

        if secrets.exists():
            load_dotenv(secrets)
        load_dotenv(envs_dir / f"{env}.env")


def get_mvp() -> Mvp:
    if Mvp.__instance__ is None:
        err = "MVP is not set up, call Mvp.setup() after FastAPI app is initialized."
        raise RuntimeError(err)
    return Mvp.__instance__


MvpDep = Annotated[Mvp, Depends(get_mvp)]
