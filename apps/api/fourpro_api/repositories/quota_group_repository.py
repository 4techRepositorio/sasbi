import uuid
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from fourpro_api.models.tenant import TenantQuotaGroup


class QuotaGroupRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def list_for_tenant(self, tenant_id: UUID) -> list[TenantQuotaGroup]:
        stmt = (
            select(TenantQuotaGroup)
            .where(TenantQuotaGroup.tenant_id == tenant_id)
            .order_by(TenantQuotaGroup.name.asc())
        )
        return list(self._db.scalars(stmt).all())

    def get(self, group_id: UUID, tenant_id: UUID) -> TenantQuotaGroup | None:
        row = self._db.get(TenantQuotaGroup, group_id)
        if row is None or row.tenant_id != tenant_id:
            return None
        return row

    def create(self, *, tenant_id: UUID, name: str, max_storage_mb: int) -> TenantQuotaGroup:
        now = datetime.now(tz=UTC)
        row = TenantQuotaGroup(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            name=name,
            max_storage_mb=max_storage_mb,
            created_at=now,
            updated_at=now,
        )
        self._db.add(row)
        self._db.commit()
        self._db.refresh(row)
        return row

    def update(
        self,
        row: TenantQuotaGroup,
        *,
        name: str | None = None,
        max_storage_mb: int | None = None,
    ) -> None:
        now = datetime.now(tz=UTC)
        if name is not None:
            row.name = name
        if max_storage_mb is not None:
            row.max_storage_mb = max_storage_mb
        row.updated_at = now
        self._db.add(row)
        self._db.commit()

    def delete(self, row: TenantQuotaGroup) -> None:
        self._db.delete(row)
        self._db.commit()
