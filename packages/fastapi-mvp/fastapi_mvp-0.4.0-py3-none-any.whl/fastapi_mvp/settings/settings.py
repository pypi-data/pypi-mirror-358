from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(from_attributes=True)

    def __hash__(self) -> int:
        return hash(self.model_dump_json())
