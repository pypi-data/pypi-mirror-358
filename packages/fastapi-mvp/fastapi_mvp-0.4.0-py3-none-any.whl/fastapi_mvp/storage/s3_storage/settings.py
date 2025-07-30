from pydantic_settings import SettingsConfigDict

from fastapi_mvp.settings import Settings


class S3Settings(Settings):
    """
    Settings that are used to configure S3 Storage.
    You can provide values explicitly or via env vars prefixed with 'S3__'.
    """

    model_config = SettingsConfigDict(
        env_prefix="S3__",
    )

    bucket: str
    host: str
    protocol: str
    region: str
    aws_access_key_id: str
    aws_secret_access_key: str
