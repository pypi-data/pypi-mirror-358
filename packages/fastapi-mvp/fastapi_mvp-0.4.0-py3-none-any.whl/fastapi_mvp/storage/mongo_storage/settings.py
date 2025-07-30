from pydantic_settings import SettingsConfigDict

from fastapi_mvp.settings import Settings


class MongoSettings(Settings):
    """
    Settings that are used to configure Mongo Storage.
    You can provide values explicitly or via env vars prefixed with 'MONGO__'.
    """

    model_config = SettingsConfigDict(
        env_prefix="MONGO__",
    )

    name: str
    user: str
    password: str
    host: str
    port: int

    def url(self) -> str:
        return f"mongodb://{self.user}:{self.password}@{self.host}:{self.port}"
