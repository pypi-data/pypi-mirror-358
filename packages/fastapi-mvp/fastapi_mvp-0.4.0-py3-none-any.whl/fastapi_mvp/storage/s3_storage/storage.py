from datetime import timedelta
from functools import lru_cache
from typing import Optional

import aiohttp
from aiobotocore.client import AioBaseClient
from aiobotocore.session import get_session
from pydantic import HttpUrl

from fastapi_mvp.storage.s3_storage.settings import S3Settings


class S3Storage:
    def __init__(self, settings: S3Settings) -> None:
        self._settings = settings
        self._client: Optional[AioBaseClient] = None

    @property
    def _endpoint_url(self) -> str:
        return f"{self._settings.protocol}://{self._settings.host}"

    async def _get_client(self) -> AioBaseClient:
        if self._client is None:
            session = get_session()
            async with session.create_client(
                "s3",
                aws_access_key_id=self._settings.aws_access_key_id,
                aws_secret_access_key=self._settings.aws_secret_access_key,
                endpoint_url=self._endpoint_url,
                region_name=self._settings.region,
            ) as client:
                self._client = client
        return self._client

    async def save(
        self,
        key: str,
        data: bytes,
        expires_in: timedelta,
    ) -> HttpUrl:
        try:
            s3 = await self._get_client()

            await s3.put_object(
                Bucket=self._settings.bucket,
                Key=key,
                Body=data,
                ContentType="application/octet-stream",
            )

            presigned_url = await s3.generate_presigned_url(
                "get_object",
                Params={"Bucket": self._settings.bucket, "Key": key},
                ExpiresIn=int(expires_in.total_seconds()),
            )
            return HttpUrl(presigned_url)
        except Exception as e:
            error_msg = f"Failed to upload data to S3: {e}"
            raise RuntimeError(error_msg) from e

    async def load_by_url(self, url: HttpUrl) -> bytes:
        try:
            async with (
                aiohttp.ClientSession(
                    raise_for_status=True,
                ) as session,
                session.get(str(url)) as resp,
            ):
                return await resp.read()
        except Exception as e:
            error_msg = f"Failed to load data by url: {e}"
            raise RuntimeError(error_msg) from e

    async def load(self, key: str) -> bytes:
        try:
            s3 = await self._get_client()

            resp = await s3.get_object(
                Bucket=self._settings.bucket,
                Key=key,
            )
            async with resp["Body"] as stream:
                return await stream.read()
        except Exception as e:
            error_msg = f"Failed to load data: {e}"
            raise RuntimeError(error_msg) from e


@lru_cache(maxsize=1)
def get_s3_storage(settings: S3Settings) -> S3Storage:
    return S3Storage(settings)
