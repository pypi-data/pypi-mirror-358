# ruff: noqa
from pydantic_settings import SettingsConfigDict

from fastapi_mvp.settings import Settings


class MetricsSettings(Settings):
    """
    Settings that are used to configure Prometheus metrics exposure.
    You can provide values explicitly or via env vars prefixed with 'METRICS__'.
    """

    model_config = SettingsConfigDict(
        env_prefix="METRICS__",
    )

    excluded_handlers: list[str] = [
        "/healthz",
        "/docs",
        "/metrics",
        "/readyz",
        "/openapi.json",
    ]
    latency_lowr_buckets: list[float] = [
        0.1,
        0.25,
        0.5,
        0.75,
        1.0,
        1.5,
        2.0,
        2.5,
        5.0,
        7.5,
        10.0,
        20.0,
        30.0,
    ]
