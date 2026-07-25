import logging

from fourpro_worker.celery_app import app

logger = logging.getLogger(__name__)


@app.task(name="fourpro.parse_ingestion")
def parse_ingestion_task(ingestion_id: str) -> str:
    from fourpro_api.jobs.ingestion_parse import run_ingestion_parse

    run_ingestion_parse(ingestion_id)
    return "ok"


@app.task(name="fourpro.sync_data_source")
def sync_data_source_task(
    sync_run_id: str,
    mode: str = "full",
    sample_limit: int = 10_000,
) -> str:
    from fourpro_api.services.data_source_service import run_data_source_sync

    run_data_source_sync(sync_run_id, mode=mode, sample_limit=sample_limit)
    return "ok"
