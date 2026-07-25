"""Repositório de data sources / credentials / sync runs."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from fourpro_api.models.data_source import ConnectorCredential, DataSource, DataSourceSyncRun

_UNSET: Any = object()


class DataSourceRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def create(
        self,
        *,
        tenant_id: UUID,
        name: str,
        connector_type: str,
        config_json: dict[str, Any],
        created_by_user_id: UUID | None,
        status: str = "ready",
    ) -> DataSource:
        now = datetime.now(tz=UTC)
        row = DataSource(
            tenant_id=tenant_id,
            name=name,
            connector_type=connector_type,
            config_json=config_json,
            status=status,
            created_by_user_id=created_by_user_id,
            created_at=now,
            updated_at=now,
        )
        self._db.add(row)
        self._db.commit()
        self._db.refresh(row)
        return row

    def get(self, data_source_id: UUID, tenant_id: UUID) -> DataSource | None:
        row = self._db.get(DataSource, data_source_id)
        if row is None or row.tenant_id != tenant_id:
            return None
        return row

    def get_by_id(self, data_source_id: UUID) -> DataSource | None:
        return self._db.get(DataSource, data_source_id)

    def list_page(
        self,
        tenant_id: UUID,
        *,
        limit: int,
        offset: int,
    ) -> tuple[list[DataSource], int]:
        filters = (DataSource.tenant_id == tenant_id,)
        total = int(
            self._db.scalar(select(func.count()).select_from(DataSource).where(*filters)) or 0
        )
        stmt = (
            select(DataSource)
            .where(*filters)
            .order_by(DataSource.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(self._db.scalars(stmt).all()), total

    def count_for_tenant(self, tenant_id: UUID) -> int:
        return int(
            self._db.scalar(
                select(func.count()).select_from(DataSource).where(DataSource.tenant_id == tenant_id)
            )
            or 0
        )

    def update(
        self,
        row: DataSource,
        *,
        name: Any = _UNSET,
        config_json: Any = _UNSET,
        status: Any = _UNSET,
        last_sync_at: Any = _UNSET,
        last_error: Any = _UNSET,
    ) -> DataSource:
        if name is not _UNSET:
            row.name = name
        if config_json is not _UNSET:
            row.config_json = config_json
        if status is not _UNSET:
            row.status = status
        if last_sync_at is not _UNSET:
            row.last_sync_at = last_sync_at
        if last_error is not _UNSET:
            row.last_error = last_error
        row.updated_at = datetime.now(tz=UTC)
        self._db.add(row)
        self._db.commit()
        self._db.refresh(row)
        return row

    def delete(self, row: DataSource) -> None:
        self._db.delete(row)
        self._db.commit()

    def has_credential(self, data_source_id: UUID, tenant_id: UUID) -> bool:
        stmt = select(ConnectorCredential.id).where(
            ConnectorCredential.data_source_id == data_source_id,
            ConnectorCredential.tenant_id == tenant_id,
        )
        return self._db.scalar(stmt) is not None

    def upsert_credential(
        self,
        *,
        tenant_id: UUID,
        data_source_id: UUID,
        secret_encrypted: str,
        key_version: int,
    ) -> ConnectorCredential:
        now = datetime.now(tz=UTC)
        existing = self._db.scalar(
            select(ConnectorCredential).where(
                ConnectorCredential.data_source_id == data_source_id,
                ConnectorCredential.tenant_id == tenant_id,
            )
        )
        if existing:
            existing.secret_encrypted = secret_encrypted
            existing.key_version = key_version
            existing.updated_at = now
            self._db.add(existing)
            self._db.commit()
            self._db.refresh(existing)
            return existing
        row = ConnectorCredential(
            tenant_id=tenant_id,
            data_source_id=data_source_id,
            secret_encrypted=secret_encrypted,
            key_version=key_version,
            created_at=now,
            updated_at=now,
        )
        self._db.add(row)
        self._db.commit()
        self._db.refresh(row)
        return row

    def get_credential(
        self, data_source_id: UUID, tenant_id: UUID
    ) -> ConnectorCredential | None:
        return self._db.scalar(
            select(ConnectorCredential).where(
                ConnectorCredential.data_source_id == data_source_id,
                ConnectorCredential.tenant_id == tenant_id,
            )
        )

    def create_sync_run(
        self,
        *,
        tenant_id: UUID,
        data_source_id: UUID,
        object_id: str | None,
        status: str = "queued",
    ) -> DataSourceSyncRun:
        now = datetime.now(tz=UTC)
        row = DataSourceSyncRun(
            tenant_id=tenant_id,
            data_source_id=data_source_id,
            object_id=object_id,
            status=status,
            created_at=now,
        )
        self._db.add(row)
        self._db.commit()
        self._db.refresh(row)
        return row

    def get_sync_run(self, sync_run_id: UUID, tenant_id: UUID | None = None) -> DataSourceSyncRun | None:
        row = self._db.get(DataSourceSyncRun, sync_run_id)
        if row is None:
            return None
        if tenant_id is not None and row.tenant_id != tenant_id:
            return None
        return row

    def get_sync_run_by_id(self, sync_run_id: UUID) -> DataSourceSyncRun | None:
        return self._db.get(DataSourceSyncRun, sync_run_id)

    def update_sync_run(
        self,
        row: DataSourceSyncRun,
        *,
        status: Any = _UNSET,
        ingestion_id: Any = _UNSET,
        friendly_message: Any = _UNSET,
        technical_log: Any = _UNSET,
        started_at: Any = _UNSET,
        finished_at: Any = _UNSET,
    ) -> DataSourceSyncRun:
        if status is not _UNSET:
            row.status = status
        if ingestion_id is not _UNSET:
            row.ingestion_id = ingestion_id
        if friendly_message is not _UNSET:
            row.friendly_message = friendly_message
        if technical_log is not _UNSET:
            row.technical_log = technical_log
        if started_at is not _UNSET:
            row.started_at = started_at
        if finished_at is not _UNSET:
            row.finished_at = finished_at
        self._db.add(row)
        self._db.commit()
        self._db.refresh(row)
        return row

    def list_sync_runs(
        self,
        tenant_id: UUID,
        data_source_id: UUID,
        *,
        limit: int,
        offset: int,
    ) -> tuple[list[DataSourceSyncRun], int]:
        filters = (
            DataSourceSyncRun.tenant_id == tenant_id,
            DataSourceSyncRun.data_source_id == data_source_id,
        )
        total = int(
            self._db.scalar(
                select(func.count()).select_from(DataSourceSyncRun).where(*filters)
            )
            or 0
        )
        stmt = (
            select(DataSourceSyncRun)
            .where(*filters)
            .order_by(DataSourceSyncRun.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(self._db.scalars(stmt).all()), total
