import os

from celery import Celery

_redis = os.environ.get("REDIS_URL", "redis://127.0.0.1:6379/0")

app = Celery(
    "fourpro_worker",
    broker=_redis,
    backend=_redis,
)

app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)


@app.task(name="fourpro.ping")
def ping() -> str:
    return "pong"


import fourpro_worker.tasks.ingestion  # noqa: E402, F401
