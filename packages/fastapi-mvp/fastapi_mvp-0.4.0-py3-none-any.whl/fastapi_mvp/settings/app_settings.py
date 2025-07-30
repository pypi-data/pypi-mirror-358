from __future__ import annotations

from typing import ClassVar, Type

from pydantic import ValidationError

from fastapi_mvp.settings.settings import Settings


class AppSettings(Settings):
    """
    Base class to inherit your application settings from.
    It ensures all settings are set eagerly during app initialization
    to avoid situations with forgotten environment variables.
    """

    __settings__: ClassVar[dict[Type[AppSettings], AppSettings]] = {}

    @classmethod
    def load_and_validate(cls) -> None:
        cls.__settings__ = cls.__load_and_validate_recursively(
            AppSettings,
            cls.__settings__,
        )

    @classmethod
    def __load_and_validate_recursively(
        cls,
        base_cls: Type[AppSettings],
        instances: dict[Type[AppSettings], AppSettings],
    ) -> dict[Type[AppSettings], AppSettings]:
        try:
            instance = base_cls()
        except ValidationError as e:
            err = (
                "Some of your application settings are not set. "
                "Check environment and defaults."
            )
            raise RuntimeError(err) from e

        instances[base_cls] = instance
        for c in base_cls.__subclasses__():
            instances.update(cls.__load_and_validate_recursively(c, instances))
        return instances
