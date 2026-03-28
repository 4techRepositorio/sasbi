from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from fourpro_api.models.ingestion import FileIngestion

_UNSET: Any = object()


class IngestionRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def create(
        self,
        *,
        tenant_id: UUID,
        original_filename: str,
        storage_path: str,
        content_type: str | None,
        size_bytes: int,
        status: str = "uploaded",
        content_sha256: str | None = None,
        uploaded_by_user_id: UUID | None = None,
    ) -> FileIngestion:
        now = datetime.now(tz=UTC)
        row = FileIngestion(
            tenant_id=tenant_id,
            original_filename=original_filename,
            storage_path=storage_path,
            content_type=content_type,
            content_sha256=content_sha256,
            uploaded_by_user_id=uploaded_by_user_id,
            size_bytes=size_bytes,
            status=status,
            created_at=now,
            updated_at=now,
        )
        self._db.add(row)
        self._db.commit()
        self._db.refresh(row)
        return row

    def get_by_id(self, ingestion_id: UUID) -> FileIngestion | None:
        return self._db.get(FileIngestion, ingestion_id)

    def get(self, ingestion_id: UUID, tenant_id: UUID) -> FileIngestion | None:
        row = self._db.get(FileIngestion, ingestion_id)
        if row is None or row.tenant_id != tenant_id:
            return None
        return row

    def update(
        self,
        row: FileIngestion,
        *,
        status: str | None = None,
        friendly_error: Any = _UNSET,
        technical_log: Any = _UNSET,
        result_summary: Any = _UNSET,
    ) -> None:
        now = datetime.now(tz=UTC)
        if status is not None:
            row.status = status
        if friendly_error is not _UNSET:
            row.friendly_error = friendly_error
        if technical_log is not _UNSET:
            row.technical_log = technical_log
        if result_summary is not _UNSET:
            row.result_summary = result_summary
        row.updated_at = now
        self._db.add(row)
        self._db.commit()

    def list_for_tenant(
        self,
        tenant_id: UUID,
        *,
        statuses: list[str] | None = None,
    ) -> list[FileIngestion]:
        stmt: Select[tuple[FileIngestion]] = select(FileIngestion).where(
            FileIngestion.tenant_id == tenant_id
        )
        if statuses:
            stmt = stmt.where(FileIngestion.status.in_(statuses))
        stmt = stmt.order_by(FileIngestion.created_at.desc())
        return list(self._db.scalars(stmt).all())

    def list_processed_page(
        self,
        tenant_id: UUID,
        *,
        limit: int,
        offset: int,
    ) -> tuple[list[FileIngestion], int]:
        filters = (
            FileIngestion.tenant_id == tenant_id,
            FileIngestion.status == "processed",
        )
        count_stmt = select(func.count()).select_from(FileIngestion).where(*filters)
        total = int(self._db.scalar(count_stmt) or 0)
        stmt = (
            select(FileIngestion)
            .where(*filters)
            .order_by(FileIngestion.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        rows = list(self._db.scalars(stmt).all())
        return rows, total

    def count_uploads_this_month(self, tenant_id: UUID) -> int:
        start = datetime.now(tz=UTC).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        stmt = (
            select(func.count())
            .select_from(FileIngestion)
            .where(
                FileIngestion.tenant_id == tenant_id,
                FileIngestion.created_at >= start,
            )
        )
        return int(self._db.scalar(stmt) or 0)

    def sum_size_bytes_for_tenant(self, tenant_id: UUID) -> int:
        stmt = select(func.coalesce(func.sum(FileIngestion.size_bytes), 0)).where(
            FileIngestion.tenant_id == tenant_id,
        )
        return int(self._db.scalar(stmt) or 0)

    def sum_size_bytes_for_user_in_tenant(self, user_id: UUID, tenant_id: UUID) -> int:
        stmt = select(func.coalesce(func.sum(FileIngestion.size_bytes), 0)).where(
            FileIngestion.tenant_id == tenant_id,
            FileIngestion.uploaded_by_user_id == user_id,
        )
        return int(self._db.scalar(stmt) or 0)

    def sum_size_bytes_for_quota_group(self, group_id: UUID, tenant_id: UUID) -> int:
        from fourpro_api.models.tenant import TenantMembership

        member_users = select(TenantMembership.user_id).where(
            TenantMembership.quota_group_id == group_id,
            TenantMembership.tenant_id == tenant_id,
        )
        stmt = select(func.coalesce(func.sum(FileIngestion.size_bytes), 0)).where(
            FileIngestion.tenant_id == tenant_id,
            FileIngestion.uploaded_by_user_id.in_(member_users),
        )
        return int(self._db.scalar(stmt) or 0)
