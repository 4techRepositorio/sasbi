import logging

from fourpro_worker.celery_app import app

logger = logging.getLogger(__name__)


@app.task(name="fourpro.parse_ingestion")
def parse_ingestion_task(ingestion_id: str, correlation_id: str | None = None) -> str:
    from fourpro_api.jobs.ingestion_parse import run_ingestion_parse

    logger.info(
        "parse_task_start",
        extra={"ingestion_id": ingestion_id, "correlation_id": correlation_id},
    )
    run_ingestion_parse(ingestion_id, correlation_id=correlation_id)
    return "ok"


@app.task(name="fourpro.sync_data_source")
def sync_data_source_task(sync_run_id: str, correlation_id: str | None = None) -> str:
    from fourpro_api.jobs.connector_sync import run_data_source_sync

    logger.info(
        "sync_task_start",
        extra={"sync_run_id": sync_run_id, "correlation_id": correlation_id},
    )
    run_data_source_sync(sync_run_id)
    return "ok"
