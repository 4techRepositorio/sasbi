from datetime import UTC, datetime
from uuid import UUID

from fastapi import HTTPException, status
from fourpro_contracts.dashboard import (
    DashboardCreate,
    DashboardItem,
    DashboardLayout,
    DashboardPatch,
    DashboardPublishResponse,
    PaginatedDashboardList,
)
from sqlalchemy.orm import Session

from fourpro_api.models.dashboard import Dashboard
from fourpro_api.repositories.dashboard_repository import DashboardRepository

_EDITABLE_STATUSES = frozenset({"draft", "published", "archived"})


def _to_item(row: Dashboard) -> DashboardItem:
    layout = DashboardLayout.model_validate(row.layout_json or {"version": 1, "widgets": []})
    return DashboardItem(
        id=str(row.id),
        tenant_id=str(row.tenant_id),
        name=row.name,
        description=row.description,
        status=row.status,  # type: ignore[arg-type]
        layout=layout,
        version=row.version,
        created_by_user_id=str(row.created_by_user_id) if row.created_by_user_id else None,
        created_at=row.created_at.isoformat(),
        updated_at=row.updated_at.isoformat(),
        published_at=row.published_at.isoformat() if row.published_at else None,
    )


class DashboardService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._repo = DashboardRepository(db)

    def create(
        self,
        tenant_id: UUID,
        user_id: UUID,
        body: DashboardCreate,
    ) -> DashboardItem:
        row = self._repo.create(
            tenant_id=tenant_id,
            name=body.name,
            description=body.description,
            layout_json=body.layout.model_dump(),
            created_by_user_id=user_id,
            status="draft",
            version=1,
        )
        return _to_item(row)

    def get(self, tenant_id: UUID, dashboard_id: UUID) -> DashboardItem:
        row = self._repo.get(dashboard_id, tenant_id)
        if row is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dashboard não encontrado",
            )
        return _to_item(row)

    def list(
        self,
        tenant_id: UUID,
        *,
        limit: int,
        offset: int,
        status_filter: str | None = None,
    ) -> PaginatedDashboardList:
        if status_filter is not None and status_filter not in _EDITABLE_STATUSES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"status inválido; use um de: {sorted(_EDITABLE_STATUSES)}",
            )
        rows, total = self._repo.list_page(
            tenant_id,
            limit=limit,
            offset=offset,
            status=status_filter,
        )
        return PaginatedDashboardList(
            items=[_to_item(r) for r in rows],
            total=total,
            limit=limit,
            offset=offset,
        )

    def patch(
        self,
        tenant_id: UUID,
        dashboard_id: UUID,
        body: DashboardPatch,
    ) -> DashboardItem:
        row = self._repo.get(dashboard_id, tenant_id)
        if row is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dashboard não encontrado",
            )
        data = body.model_dump(exclude_unset=True)
        kwargs: dict = {}
        if "name" in data:
            kwargs["name"] = data["name"]
        if "description" in data:
            kwargs["description"] = data["description"]
        if "layout" in data and data["layout"] is not None:
            kwargs["layout_json"] = DashboardLayout.model_validate(data["layout"]).model_dump()
        if "status" in data and data["status"] is not None:
            if data["status"] not in _EDITABLE_STATUSES:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="status inválido",
                )
            kwargs["status"] = data["status"]
        if kwargs:
            row = self._repo.update(row, **kwargs)
        return _to_item(row)

    def delete(self, tenant_id: UUID, dashboard_id: UUID) -> None:
        row = self._repo.get(dashboard_id, tenant_id)
        if row is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dashboard não encontrado",
            )
        self._repo.delete(row)

    def publish(self, tenant_id: UUID, dashboard_id: UUID) -> DashboardPublishResponse:
        row = self._repo.get(dashboard_id, tenant_id)
        if row is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dashboard não encontrado",
            )
        if row.status == "archived":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Dashboard arquivado não pode ser publicado",
            )

        now = datetime.now(tz=UTC)
        # Bump version on re-publish; first publish keeps version 1
        new_version = row.version + 1 if row.status == "published" else max(row.version, 1)
        layout_snapshot = dict(row.layout_json or {})
        self._repo.add_version(
            dashboard_id=row.id,
            version=new_version,
            layout_json=layout_snapshot,
        )
        updated = self._repo.update(
            row,
            status="published",
            version=new_version,
            published_at=now,
        )
        assert updated.published_at is not None
        return DashboardPublishResponse(
            id=str(updated.id),
            status="published",
            version=updated.version,
            published_at=updated.published_at.isoformat(),
        )
