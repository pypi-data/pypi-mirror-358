from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from pydantic_settings import BaseSettings


class LoadEnvSettings(BaseSettings):
    """
    Settings to configure loading environment variables from .env file.
    Secrets are read from another file if it exists.
    Values from secrets override values from .env file but not from the system.
    """

    env: str
    envs_dir: Optional[Path] = None
    secrets: Optional[Path] = None

    def load(self) -> None:
        envs_dir = self.envs_dir or Path("envs")
        secrets = self.secrets or (envs_dir / "secrets.env")

        if secrets.exists():
            load_dotenv(secrets)
        load_dotenv(envs_dir / f"{self.env}.env")
