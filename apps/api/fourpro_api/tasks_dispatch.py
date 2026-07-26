import logging
import os

from celery import Celery

from fourpro_api.config import get_settings
from fourpro_api.middleware.correlation import get_correlation_id

logger = logging.getLogger(__name__)

_celery_app: Celery | None = None


def _sync_fallback_enabled() -> bool:
    return os.environ.get("INGESTION_SYNC_PARSE_FALLBACK", "").lower() in ("1", "true", "yes")


def _get_celery_app(redis_url: str) -> Celery:
    global _celery_app
    if _celery_app is None:
        _celery_app = Celery(broker=redis_url, backend=redis_url)
    return _celery_app


def enqueue_ingestion_parse(ingestion_id: str, *, correlation_id: str | None = None) -> None:
    """Envia parse para Celery com correlation_id (TICKET-013)."""
    cid = correlation_id or get_correlation_id()
    settings = get_settings()
    if settings.redis_url:
        try:
            app = _get_celery_app(settings.redis_url)
            app.send_task(
                "fourpro.parse_ingestion",
                args=[ingestion_id],
                kwargs={"correlation_id": cid},
            )
            logger.info(
                "ingestion_enqueued",
                extra={"id": ingestion_id, "correlation_id": cid},
            )
            return
        except Exception:
            logger.exception("celery_enqueue_failed")
    if _sync_fallback_enabled():
        logger.info(
            "ingestion_parse_sync_fallback",
            extra={"id": ingestion_id, "correlation_id": cid},
        )
        from fourpro_api.jobs.ingestion_parse import run_ingestion_parse

        run_ingestion_parse(ingestion_id, correlation_id=cid)


def enqueue_data_source_sync(
    sync_run_id: str,
    *,
    correlation_id: str | None = None,
    db=None,
) -> None:
    cid = correlation_id or get_correlation_id()
    if _sync_fallback_enabled():
        from fourpro_api.jobs.connector_sync import run_data_source_sync

        run_data_source_sync(sync_run_id, db=db)
        return
    settings = get_settings()
    if settings.redis_url:
        try:
            app = _get_celery_app(settings.redis_url)
            app.send_task(
                "fourpro.sync_data_source",
                args=[sync_run_id],
                kwargs={"correlation_id": cid},
            )
            logger.info(
                "sync_enqueued",
                extra={"id": sync_run_id, "correlation_id": cid},
            )
            return
        except Exception:
            logger.exception("celery_sync_enqueue_failed")
    from fourpro_api.jobs.connector_sync import run_data_source_sync

    run_data_source_sync(sync_run_id, db=db)
