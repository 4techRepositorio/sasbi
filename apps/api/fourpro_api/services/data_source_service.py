"""Serviço de fontes de dados / sync (TICKET-015)."""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

from fastapi import HTTPException, status
from fourpro_contracts.connectors import (
    ConnectionTestResult,
    ConnectorCatalogResponse,
    DataSourceCreate,
    DataSourceItem,
    DataSourcePatch,
    DiscoverResponse,
    PaginatedDataSourceList,
    PaginatedSyncRunList,
    SampleSchemaResponse,
    SyncEnqueuedResponse,
    SyncRequest,
    SyncRunItem,
)
from fourpro_connectors import get_connector, list_capabilities
from fourpro_connectors.base import ConnectorError
from sqlalchemy.orm import Session

from fourpro_api.config import get_settings
from fourpro_api.core.principal import Principal
from fourpro_api.models.data_source import DataSource, DataSourceSyncRun
from fourpro_api.repositories.audit_repository import AuditAction, AuditRepository
from fourpro_api.repositories.data_source_repository import DataSourceRepository
from fourpro_api.repositories.ingestion_repository import IngestionRepository
from fourpro_api.services.billing_service import BillingService
from fourpro_api.services.credential_vault import CredentialVault
from fourpro_api.tasks_dispatch import enqueue_data_source_sync, enqueue_ingestion_parse

logger = logging.getLogger(__name__)


class DataSourceService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._repo = DataSourceRepository(db)
        self._vault = CredentialVault()
        self._audit = AuditRepository(db)
        self._billing = BillingService(db)

    def catalog(self) -> ConnectorCatalogResponse:
        return ConnectorCatalogResponse(items=list_capabilities())

    def _to_item(self, row: DataSource) -> DataSourceItem:
        has_secret = self._repo.has_credential(row.id, row.tenant_id)
        return DataSourceItem(
            id=str(row.id),
            tenant_id=str(row.tenant_id),
            name=row.name,
            connector_type=row.connector_type,  # type: ignore[arg-type]
            config=dict(row.config_json or {}),
            status=row.status,  # type: ignore[arg-type]
            has_secret=has_secret,
            last_sync_at=row.last_sync_at.isoformat() if row.last_sync_at else None,
            last_error=row.last_error,
            created_by_user_id=str(row.created_by_user_id) if row.created_by_user_id else None,
            created_at=row.created_at.isoformat(),
            updated_at=row.updated_at.isoformat(),
        )

    def _to_sync_item(self, row: DataSourceSyncRun) -> SyncRunItem:
        return SyncRunItem(
            id=str(row.id),
            tenant_id=str(row.tenant_id),
            data_source_id=str(row.data_source_id),
            ingestion_id=str(row.ingestion_id) if row.ingestion_id else None,
            status=row.status,  # type: ignore[arg-type]
            object_id=row.object_id,
            friendly_message=row.friendly_message,
            technical_log=row.technical_log,
            started_at=row.started_at.isoformat() if row.started_at else None,
            finished_at=row.finished_at.isoformat() if row.finished_at else None,
            created_at=row.created_at.isoformat(),
        )

    def _load_secret(self, data_source_id: UUID, tenant_id: UUID) -> dict[str, str] | None:
        cred = self._repo.get_credential(data_source_id, tenant_id)
        if cred is None:
            return None
        return self._vault.decrypt_dict(cred.secret_encrypted)

    def _get_or_404(self, data_source_id: UUID, tenant_id: UUID) -> DataSource:
        row = self._repo.get(data_source_id, tenant_id)
        if row is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fonte não encontrada")
        return row

    def list_sources(
        self, principal: Principal, *, limit: int, offset: int
    ) -> PaginatedDataSourceList:
        rows, total = self._repo.list_page(principal.tenant_id, limit=limit, offset=offset)
        return PaginatedDataSourceList(
            items=[self._to_item(r) for r in rows],
            total=total,
            limit=limit,
            offset=offset,
        )

    def create(self, principal: Principal, body: DataSourceCreate) -> DataSourceItem:
        self._billing.ensure_data_source_allowed(principal.tenant_id)
        try:
            connector = get_connector(body.connector_type)
            connector.validate_config(body.config, body.secret)
        except KeyError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Tipo de conector inválido"
            ) from e
        except (ConnectorError, ValueError) as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e

        row = self._repo.create(
            tenant_id=principal.tenant_id,
            name=body.name,
            connector_type=body.connector_type,
            config_json=body.config,
            created_by_user_id=principal.user_id,
        )
        if body.secret:
            token = self._vault.encrypt_dict(body.secret)
            self._repo.upsert_credential(
                tenant_id=principal.tenant_id,
                data_source_id=row.id,
                secret_encrypted=token,
                key_version=self._vault.key_version,
            )
        self._audit.record(
            action=AuditAction.DATA_SOURCE_CREATED,
            actor_user_id=principal.user_id,
            tenant_id=principal.tenant_id,
            context={
                "data_source_id": str(row.id),
                "connector_type": body.connector_type,
                "has_secret": bool(body.secret),
            },
        )
        return self._to_item(row)

    def get(self, principal: Principal, data_source_id: UUID) -> DataSourceItem:
        return self._to_item(self._get_or_404(data_source_id, principal.tenant_id))

    def patch(
        self, principal: Principal, data_source_id: UUID, body: DataSourcePatch
    ) -> DataSourceItem:
        row = self._get_or_404(data_source_id, principal.tenant_id)
        config = body.config if body.config is not None else dict(row.config_json or {})
        secret = body.secret
        if body.config is not None or body.secret is not None:
            try:
                connector = get_connector(row.connector_type)
                existing_secret = secret if secret is not None else self._load_secret(row.id, row.tenant_id)
                connector.validate_config(config, existing_secret)
            except (ConnectorError, ValueError) as e:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e

        kwargs: dict[str, Any] = {}
        if body.name is not None:
            kwargs["name"] = body.name
        if body.config is not None:
            kwargs["config_json"] = body.config
        if body.status is not None:
            kwargs["status"] = body.status
        if kwargs:
            row = self._repo.update(row, **kwargs)
        if body.secret is not None:
            token = self._vault.encrypt_dict(body.secret)
            self._repo.upsert_credential(
                tenant_id=principal.tenant_id,
                data_source_id=row.id,
                secret_encrypted=token,
                key_version=self._vault.key_version,
            )
        return self._to_item(row)

    def delete(self, principal: Principal, data_source_id: UUID) -> None:
        row = self._get_or_404(data_source_id, principal.tenant_id)
        self._repo.delete(row)

    def test_connection(self, principal: Principal, data_source_id: UUID) -> ConnectionTestResult:
        row = self._get_or_404(data_source_id, principal.tenant_id)
        secret = self._load_secret(row.id, row.tenant_id)
        connector = get_connector(row.connector_type)
        result = connector.test_connection(dict(row.config_json or {}), secret)
        self._audit.record(
            action=AuditAction.DATA_SOURCE_TESTED,
            actor_user_id=principal.user_id,
            tenant_id=principal.tenant_id,
            context={"data_source_id": str(row.id), "ok": result.ok},
        )
        return result

    def discover(self, principal: Principal, data_source_id: UUID) -> DiscoverResponse:
        row = self._get_or_404(data_source_id, principal.tenant_id)
        secret = self._load_secret(row.id, row.tenant_id)
        connector = get_connector(row.connector_type)
        try:
            return connector.discover(dict(row.config_json or {}), secret)
        except ConnectorError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message) from e

    def sample_schema(
        self,
        principal: Principal,
        data_source_id: UUID,
        *,
        object_id: str,
        limit: int = 100,
    ) -> SampleSchemaResponse:
        row = self._get_or_404(data_source_id, principal.tenant_id)
        secret = self._load_secret(row.id, row.tenant_id)
        connector = get_connector(row.connector_type)
        try:
            return connector.sample_schema(
                dict(row.config_json or {}),
                secret,
                object_id=object_id,
                limit=limit,
            )
        except ConnectorError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message) from e

    def enqueue_sync(
        self, principal: Principal, data_source_id: UUID, body: SyncRequest
    ) -> SyncEnqueuedResponse:
        row = self._get_or_404(data_source_id, principal.tenant_id)
        if row.status == "disabled":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Fonte desactivada"
            )
        run = self._repo.create_sync_run(
            tenant_id=principal.tenant_id,
            data_source_id=row.id,
            object_id=body.object_id,
            status="queued",
        )
        # Guardar params de sync no technical_log inicial (JSON curto) — worker lê object_id + defaults
        self._repo.update_sync_run(
            run,
            technical_log=f"mode={body.mode};sample_limit={body.sample_limit}",
        )
        self._repo.update(row, status="syncing", last_error=None)
        self._audit.record(
            action=AuditAction.DATA_SOURCE_SYNC_ENQUEUED,
            actor_user_id=principal.user_id,
            tenant_id=principal.tenant_id,
            context={
                "data_source_id": str(row.id),
                "sync_run_id": str(run.id),
                "object_id": body.object_id,
            },
        )
        enqueue_data_source_sync(
            str(run.id),
            mode=body.mode,
            sample_limit=body.sample_limit,
            db=self._db,
        )
        return SyncEnqueuedResponse(sync_run_id=str(run.id))

    def list_sync_runs(
        self,
        principal: Principal,
        data_source_id: UUID,
        *,
        limit: int,
        offset: int,
    ) -> PaginatedSyncRunList:
        self._get_or_404(data_source_id, principal.tenant_id)
        rows, total = self._repo.list_sync_runs(
            principal.tenant_id, data_source_id, limit=limit, offset=offset
        )
        return PaginatedSyncRunList(
            items=[self._to_sync_item(r) for r in rows],
            total=total,
            limit=limit,
            offset=offset,
        )


def run_data_source_sync(
    sync_run_id: str,
    *,
    mode: str = "full",
    sample_limit: int = 10_000,
    db: Session | None = None,
) -> None:
    """Worker entry: extract → FileIngestion → parse pipeline."""
    from fourpro_api.db.session import get_session_maker
    from fourpro_api.jobs.ingestion_parse import run_ingestion_parse

    own = db is None
    if own:
        db = get_session_maker()()
    assert db is not None
    repo = DataSourceRepository(db)
    vault = CredentialVault()
    try:
        run = repo.get_sync_run_by_id(UUID(sync_run_id))
        if run is None:
            logger.warning("sync_run_not_found", extra={"id": sync_run_id})
            return
        ds = repo.get_by_id(run.data_source_id)
        if ds is None or ds.tenant_id != run.tenant_id:
            repo.update_sync_run(
                run,
                status="failed",
                friendly_message="Fonte de dados em falta",
                finished_at=datetime.now(tz=UTC),
            )
            return

        now = datetime.now(tz=UTC)
        repo.update_sync_run(run, status="running", started_at=now)

        secret = None
        cred = repo.get_credential(ds.id, ds.tenant_id)
        if cred is not None:
            secret = vault.decrypt_dict(cred.secret_encrypted)

        settings = get_settings()
        stage_dir = Path(settings.upload_dir) / str(ds.tenant_id) / "connector_stage"
        stage_dir.mkdir(parents=True, exist_ok=True)
        ext_guess = "json" if ds.connector_type == "rest_json" else "csv"
        stage_file = stage_dir / f"{uuid4()}_extract.{ext_guess}"

        try:
            connector = get_connector(ds.connector_type)
            result = connector.extract(
                dict(ds.config_json or {}),
                secret,
                stage_path=stage_file,
                object_id=run.object_id,
                mode=mode if mode in ("full", "sample") else "full",  # type: ignore[arg-type]
                sample_limit=sample_limit,
            )
        except ConnectorError as e:
            repo.update_sync_run(
                run,
                status="failed",
                friendly_message=e.message,
                technical_log=e.technical,
                finished_at=datetime.now(tz=UTC),
            )
            repo.update(ds, status="error", last_error=e.message)
            return
        except Exception as e:  # noqa: BLE001
            msg = "Falha na extracção"
            repo.update_sync_run(
                run,
                status="failed",
                friendly_message=msg,
                technical_log=f"{type(e).__name__}: {e}",
                finished_at=datetime.now(tz=UTC),
            )
            repo.update(ds, status="error", last_error=msg)
            logger.exception("data_source_extract_failed", extra={"sync_run_id": sync_run_id})
            return

        # Rename stage to final extension if needed
        final_path = result.stage_path
        ingestions = IngestionRepository(db)
        ing = ingestions.create(
            tenant_id=ds.tenant_id,
            original_filename=result.original_filename,
            storage_path=str(final_path),
            content_type=result.content_type,
            size_bytes=result.size_bytes,
            status="uploaded",
            uploaded_by_user_id=ds.created_by_user_id,
        )
        repo.update_sync_run(
            run,
            status="uploaded",
            ingestion_id=ing.id,
            friendly_message="Extract concluído; a processar ingestão",
            technical_log=f"rows={result.row_count};format={result.format}",
        )
        repo.update(ds, status="ready", last_sync_at=datetime.now(tz=UTC), last_error=None)

        run_ingestion_parse(str(ing.id), db=db)

        # Reflect final ingestion status on sync run
        db.refresh(ing)
        finished = datetime.now(tz=UTC)
        sync_status = ing.status if ing.status in ("processed", "failed") else "parsing"
        repo.update_sync_run(
            run,
            status=sync_status,
            friendly_message=ing.friendly_error or "Sincronização concluída",
            finished_at=finished if sync_status in ("processed", "failed") else None,
        )
        if ing.status == "failed":
            repo.update(ds, status="error", last_error=ing.friendly_error)
        else:
            # Ainda enfileirar se parse não correu sync (raro neste path)
            if ing.status == "uploaded":
                enqueue_ingestion_parse(str(ing.id))
    finally:
        if own:
            db.close()
