"""Job de sync de data source → ingestão (TICKET-015)."""

from __future__ import annotations

import logging
from pathlib import Path
from uuid import UUID, uuid4

from fourpro_connectors import get_connector
from fourpro_connectors.spi import ConnectorContext
from sqlalchemy.orm import Session

from fourpro_api.config import get_settings
from fourpro_api.db.session import get_session_maker
from fourpro_api.repositories.data_source_repository import DataSourceRepository
from fourpro_api.repositories.ingestion_repository import IngestionRepository
from fourpro_api.tasks_dispatch import enqueue_ingestion_parse

logger = logging.getLogger(__name__)


def run_data_source_sync(sync_run_id: str, *, db: Session | None = None) -> None:
    own = db is None
    if own:
        db = get_session_maker()()
    assert db is not None
    repo = DataSourceRepository(db)
    try:
        run = repo.get_sync_run(UUID(sync_run_id))
        if run is None:
            logger.warning("sync_run_not_found", extra={"id": sync_run_id})
            return
        repo.update_sync_run(run, status="running")
        src = repo.get(run.data_source_id, run.tenant_id)
        if src is None:
            repo.update_sync_run(
                run,
                status="failed",
                friendly_error="Fonte não encontrada",
                technical_log="data_source missing",
            )
            return
        connector = get_connector(src.connector_type)
        if connector is None:
            repo.update_sync_run(
                run,
                status="failed",
                friendly_error="Tipo de conector desconhecido",
                technical_log=src.connector_type,
            )
            return
        secret = repo.get_secret(src.id, src.tenant_id)
        ctx = ConnectorContext(
            tenant_id=str(src.tenant_id),
            data_source_id=str(src.id),
            config=dict(src.config_json or {}),
            secret=secret,
            correlation_id=run.correlation_id,
        )
        # Offline-friendly: REST demo_fallback se configurado
        if src.connector_type == "rest_json" and "demo_fallback" not in ctx.config:
            ctx.config["demo_fallback"] = True
        result = connector.extract(ctx)
        if not result.ok or not result.payload_bytes:
            repo.update_sync_run(
                run,
                status="failed",
                friendly_error=result.message,
                technical_log=result.message,
            )
            src.status = "error"
            db.add(src)
            db.commit()
            return
        settings = get_settings()
        base = Path(settings.upload_dir) / str(src.tenant_id) / "connectors"
        base.mkdir(parents=True, exist_ok=True)
        filename = result.filename or f"{src.connector_type}.json"
        dest = base / f"{uuid4()}_{filename}"
        dest.write_bytes(result.payload_bytes)
        ing_repo = IngestionRepository(db)
        ing = ing_repo.create(
            tenant_id=src.tenant_id,
            original_filename=filename,
            storage_path=str(dest.resolve()),
            content_type=result.content_type,
            size_bytes=len(result.payload_bytes),
            status="uploaded",
            uploaded_by_user_id=src.created_by_user_id,
            layer="bronze",
            correlation_id=run.correlation_id,
            technical_log=f"sync connector={src.connector_type} run={run.id}",
        )
        repo.update_sync_run(run, status="processed", ingestion_id=ing.id)
        # Com sessão injectada (testes), parse na mesma ligação; senão fila/fallback.
        if not own:
            from fourpro_api.jobs.ingestion_parse import run_ingestion_parse

            run_ingestion_parse(str(ing.id), db=db, correlation_id=run.correlation_id)
        else:
            enqueue_ingestion_parse(str(ing.id), correlation_id=run.correlation_id)
        logger.info(
            "connector_sync_ok",
            extra={
                "correlation_id": run.correlation_id,
                "ingestion_id": str(ing.id),
                "data_source_id": str(src.id),
            },
        )
    finally:
        if own:
            db.close()
