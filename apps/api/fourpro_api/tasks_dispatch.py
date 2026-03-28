import logging

from fourpro_api.config import get_settings

logger = logging.getLogger(__name__)


def enqueue_ingestion_parse(ingestion_id: str) -> None:
    settings = get_settings()
    if settings.redis_url:
        try:
            from celery import Celery

            app = Celery(broker=settings.redis_url, backend=settings.redis_url)
            app.send_task("fourpro.parse_ingestion", args=[ingestion_id])
            logger.info("ingestion_enqueued", extra={"id": ingestion_id})
        except Exception:
            logger.exception("celery_enqueue_failed")
            from fourpro_api.jobs.ingestion_parse import run_ingestion_parse

            run_ingestion_parse(ingestion_id)
    else:
        from fourpro_api.jobs.ingestion_parse import run_ingestion_parse

        run_ingestion_parse(ingestion_id)
