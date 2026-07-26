from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from fourpro_api.models.dashboard import Dashboard, DashboardWidget


class DashboardRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def list_page(
        self, tenant_id: UUID, *, limit: int, offset: int
    ) -> tuple[list[Dashboard], int]:
        filters = (Dashboard.tenant_id == tenant_id,)
        total = int(
            self._db.scalar(select(func.count()).select_from(Dashboard).where(*filters)) or 0
        )
        rows = list(
            self._db.scalars(
                select(Dashboard)
                .where(*filters)
                .options(selectinload(Dashboard.widgets))
                .order_by(Dashboard.updated_at.desc())
                .limit(limit)
                .offset(offset)
            ).all()
        )
        return rows, total

    def get(self, dashboard_id: UUID, tenant_id: UUID) -> Dashboard | None:
        row = self._db.scalar(
            select(Dashboard)
            .where(Dashboard.id == dashboard_id, Dashboard.tenant_id == tenant_id)
            .options(selectinload(Dashboard.widgets))
        )
        return row

    def create(
        self,
        *,
        tenant_id: UUID,
        title: str,
        description: str | None,
        layout_json: dict[str, Any],
        created_by_user_id: UUID | None,
        widgets: list[dict[str, Any]],
    ) -> Dashboard:
        now = datetime.now(tz=UTC)
        dash = Dashboard(
            tenant_id=tenant_id,
            title=title,
            description=description,
            layout_json=layout_json or {},
            created_by_user_id=created_by_user_id,
            created_at=now,
            updated_at=now,
        )
        self._db.add(dash)
        self._db.flush()
        for i, w in enumerate(widgets):
            self._db.add(
                DashboardWidget(
                    dashboard_id=dash.id,
                    tenant_id=tenant_id,
                    widget_type=w["widget_type"],
                    title=w["title"],
                    dataset_id=UUID(w["dataset_id"]) if w.get("dataset_id") else None,
                    config=w.get("config") or {},
                    position=w.get("position") or {},
                    sort_order=i,
                )
            )
        self._db.commit()
        return self.get(dash.id, tenant_id)  # type: ignore[return-value]

    def replace_widgets(
        self, dash: Dashboard, widgets: list[dict[str, Any]]
    ) -> Dashboard:
        for existing in list(dash.widgets):
            self._db.delete(existing)
        self._db.flush()
        for i, w in enumerate(widgets):
            self._db.add(
                DashboardWidget(
                    dashboard_id=dash.id,
                    tenant_id=dash.tenant_id,
                    widget_type=w["widget_type"],
                    title=w["title"],
                    dataset_id=UUID(w["dataset_id"]) if w.get("dataset_id") else None,
                    config=w.get("config") or {},
                    position=w.get("position") or {},
                    sort_order=i,
                )
            )
        dash.updated_at = datetime.now(tz=UTC)
        self._db.add(dash)
        self._db.commit()
        return self.get(dash.id, dash.tenant_id)  # type: ignore[return-value]

    def update_meta(
        self,
        dash: Dashboard,
        *,
        title: str | None = None,
        description: str | None = None,
        layout_json: dict[str, Any] | None = None,
    ) -> Dashboard:
        if title is not None:
            dash.title = title
        if description is not None:
            dash.description = description
        if layout_json is not None:
            dash.layout_json = layout_json
        dash.updated_at = datetime.now(tz=UTC)
        self._db.add(dash)
        self._db.commit()
        return self.get(dash.id, dash.tenant_id)  # type: ignore[return-value]

    def delete(self, dash: Dashboard) -> None:
        self._db.delete(dash)
        self._db.commit()
