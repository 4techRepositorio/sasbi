import logging

from fourpro_worker.celery_app import app

logger = logging.getLogger(__name__)


@app.task(name="fourpro.parse_ingestion")
def parse_ingestion_task(ingestion_id: str) -> str:
    from fourpro_api.jobs.ingestion_parse import run_ingestion_parse

    run_ingestion_parse(ingestion_id)
    return "ok"
