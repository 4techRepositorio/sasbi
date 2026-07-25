from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from fourpro_api.models.dashboard import Dashboard, DashboardVersion

_UNSET: Any = object()


class DashboardRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def create(
        self,
        *,
        tenant_id: UUID,
        name: str,
        description: str | None,
        layout_json: dict[str, Any],
        created_by_user_id: UUID | None,
        status: str = "draft",
        version: int = 1,
    ) -> Dashboard:
        now = datetime.now(tz=UTC)
        row = Dashboard(
            tenant_id=tenant_id,
            name=name,
            description=description,
            status=status,
            layout_json=layout_json,
            version=version,
            created_by_user_id=created_by_user_id,
            published_at=None,
            created_at=now,
            updated_at=now,
        )
        self._db.add(row)
        self._db.commit()
        self._db.refresh(row)
        return row

    def get(self, dashboard_id: UUID, tenant_id: UUID) -> Dashboard | None:
        row = self._db.get(Dashboard, dashboard_id)
        if row is None or row.tenant_id != tenant_id:
            return None
        return row

    def list_page(
        self,
        tenant_id: UUID,
        *,
        limit: int,
        offset: int,
        status: str | None = None,
    ) -> tuple[list[Dashboard], int]:
        filters = [Dashboard.tenant_id == tenant_id]
        if status is not None:
            filters.append(Dashboard.status == status)
        total = int(
            self._db.scalar(select(func.count()).select_from(Dashboard).where(*filters)) or 0
        )
        stmt: Select[tuple[Dashboard]] = (
            select(Dashboard)
            .where(*filters)
            .order_by(Dashboard.updated_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(self._db.scalars(stmt).all()), total

    def update(
        self,
        row: Dashboard,
        *,
        name: Any = _UNSET,
        description: Any = _UNSET,
        layout_json: Any = _UNSET,
        status: Any = _UNSET,
        version: Any = _UNSET,
        published_at: Any = _UNSET,
    ) -> Dashboard:
        if name is not _UNSET:
            row.name = name
        if description is not _UNSET:
            row.description = description
        if layout_json is not _UNSET:
            row.layout_json = layout_json
        if status is not _UNSET:
            row.status = status
        if version is not _UNSET:
            row.version = version
        if published_at is not _UNSET:
            row.published_at = published_at
        row.updated_at = datetime.now(tz=UTC)
        self._db.add(row)
        self._db.commit()
        self._db.refresh(row)
        return row

    def delete(self, row: Dashboard) -> None:
        self._db.delete(row)
        self._db.commit()

    def add_version(
        self,
        *,
        dashboard_id: UUID,
        version: int,
        layout_json: dict[str, Any],
    ) -> DashboardVersion:
        snap = DashboardVersion(
            dashboard_id=dashboard_id,
            version=version,
            layout_json=layout_json,
            created_at=datetime.now(tz=UTC),
        )
        self._db.add(snap)
        self._db.commit()
        self._db.refresh(snap)
        return snap
