import logging
import os

from celery import Celery

from fourpro_api.config import get_settings

logger = logging.getLogger(__name__)

_celery_app: Celery | None = None


def _sync_fallback_enabled() -> bool:
    return os.environ.get("INGESTION_SYNC_PARSE_FALLBACK", "").lower() in ("1", "true", "yes")


def _get_celery_app(redis_url: str) -> Celery:
    global _celery_app
    if _celery_app is None:
        _celery_app = Celery(broker=redis_url, backend=redis_url)
    return _celery_app


def enqueue_ingestion_parse(ingestion_id: str) -> None:
    """Envia parse para Celery.

    Sem Redis só corre em processo se INGESTION_SYNC_PARSE_FALLBACK estiver ativo.
    """
    settings = get_settings()
    if settings.redis_url:
        try:
            app = _get_celery_app(settings.redis_url)
            app.send_task("fourpro.parse_ingestion", args=[ingestion_id])
            logger.info("ingestion_enqueued", extra={"id": ingestion_id})
            return
        except Exception:
            logger.exception("celery_enqueue_failed")
    if _sync_fallback_enabled():
        logger.info("ingestion_parse_sync_fallback", extra={"id": ingestion_id})
        from fourpro_api.jobs.ingestion_parse import run_ingestion_parse

        run_ingestion_parse(ingestion_id)
