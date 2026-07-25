from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from fourpro_api.models.data_source import ConnectorCredential, DataSource, DataSourceSyncRun
from fourpro_api.services.credential_vault import decrypt_secret, encrypt_secret


class DataSourceRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def list_page(
        self, tenant_id: UUID, *, limit: int, offset: int
    ) -> tuple[list[DataSource], int]:
        filters = (DataSource.tenant_id == tenant_id,)
        total = int(
            self._db.scalar(select(func.count()).select_from(DataSource).where(*filters)) or 0
        )
        rows = list(
            self._db.scalars(
                select(DataSource)
                .where(*filters)
                .order_by(DataSource.updated_at.desc())
                .limit(limit)
                .offset(offset)
            ).all()
        )
        return rows, total

    def get(self, source_id: UUID, tenant_id: UUID) -> DataSource | None:
        row = self._db.get(DataSource, source_id)
        if row is None or row.tenant_id != tenant_id:
            return None
        return row

    def has_secret(self, data_source_id: UUID) -> bool:
        row = self._db.scalar(
            select(ConnectorCredential).where(ConnectorCredential.data_source_id == data_source_id)
        )
        return row is not None

    def get_secret(self, data_source_id: UUID, tenant_id: UUID) -> str | None:
        row = self._db.scalar(
            select(ConnectorCredential).where(
                ConnectorCredential.data_source_id == data_source_id,
                ConnectorCredential.tenant_id == tenant_id,
            )
        )
        if row is None:
            return None
        return decrypt_secret(row.secret_encrypted)

    def create(
        self,
        *,
        tenant_id: UUID,
        name: str,
        connector_type: str,
        config: dict[str, Any],
        created_by_user_id: UUID | None,
        secret: str | None,
    ) -> DataSource:
        now = datetime.now(tz=UTC)
        src = DataSource(
            tenant_id=tenant_id,
            name=name,
            connector_type=connector_type,
            config_json=config or {},
            status="active",
            created_by_user_id=created_by_user_id,
            created_at=now,
            updated_at=now,
        )
        self._db.add(src)
        self._db.flush()
        if secret:
            self._db.add(
                ConnectorCredential(
                    tenant_id=tenant_id,
                    data_source_id=src.id,
                    secret_encrypted=encrypt_secret(secret),
                    key_version="v1",
                    created_at=now,
                    updated_at=now,
                )
            )
        self._db.commit()
        self._db.refresh(src)
        return src

    def update(
        self,
        src: DataSource,
        *,
        name: str | None = None,
        config: dict[str, Any] | None = None,
        status: str | None = None,
        secret: str | None = None,
    ) -> DataSource:
        if name is not None:
            src.name = name
        if config is not None:
            src.config_json = config
        if status is not None:
            src.status = status
        src.updated_at = datetime.now(tz=UTC)
        self._db.add(src)
        if secret is not None:
            cred = self._db.scalar(
                select(ConnectorCredential).where(ConnectorCredential.data_source_id == src.id)
            )
            now = datetime.now(tz=UTC)
            if cred is None:
                self._db.add(
                    ConnectorCredential(
                        tenant_id=src.tenant_id,
                        data_source_id=src.id,
                        secret_encrypted=encrypt_secret(secret),
                        key_version="v1",
                        created_at=now,
                        updated_at=now,
                    )
                )
            else:
                cred.secret_encrypted = encrypt_secret(secret)
                cred.updated_at = now
                self._db.add(cred)
        self._db.commit()
        self._db.refresh(src)
        return src

    def delete(self, src: DataSource) -> None:
        self._db.delete(src)
        self._db.commit()

    def create_sync_run(
        self,
        *,
        tenant_id: UUID,
        data_source_id: UUID,
        correlation_id: str | None,
        status: str = "queued",
    ) -> DataSourceSyncRun:
        now = datetime.now(tz=UTC)
        run = DataSourceSyncRun(
            tenant_id=tenant_id,
            data_source_id=data_source_id,
            status=status,
            correlation_id=correlation_id,
            created_at=now,
            updated_at=now,
        )
        self._db.add(run)
        self._db.commit()
        self._db.refresh(run)
        return run

    def get_sync_run(self, run_id: UUID) -> DataSourceSyncRun | None:
        return self._db.get(DataSourceSyncRun, run_id)

    def update_sync_run(self, run: DataSourceSyncRun, **fields: Any) -> None:
        for k, v in fields.items():
            setattr(run, k, v)
        run.updated_at = datetime.now(tz=UTC)
        self._db.add(run)
        self._db.commit()

    def list_sync_runs(
        self, data_source_id: UUID, tenant_id: UUID, *, limit: int = 50
    ) -> list[DataSourceSyncRun]:
        return list(
            self._db.scalars(
                select(DataSourceSyncRun)
                .where(
                    DataSourceSyncRun.data_source_id == data_source_id,
                    DataSourceSyncRun.tenant_id == tenant_id,
                )
                .order_by(DataSourceSyncRun.created_at.desc())
                .limit(limit)
            ).all()
        )
