from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from fastapi_mvp.metrics.settings import MetricsSettings


def instrument_app(app: FastAPI, metrics_settings: MetricsSettings) -> None:
    instrumentator = Instrumentator(
        should_group_status_codes=False,
        excluded_handlers=metrics_settings.excluded_handlers,
    ).instrument(app, latency_lowr_buckets=metrics_settings.latency_lowr_buckets)
    instrumentator.expose(app)
