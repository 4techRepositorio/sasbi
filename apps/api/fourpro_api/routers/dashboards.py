from __future__ import annotations

from datetime import UTC, datetime
from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fourpro_contracts.dashboard import (
    DashboardCreate,
    DashboardDetail,
    DashboardExportPackage,
    DashboardSummary,
    DashboardUpdate,
    DashboardWidgetOut,
    PaginatedDashboardList,
)
from sqlalchemy.orm import Session

from fourpro_api.core.principal import Principal
from fourpro_api.db.session import get_db
from fourpro_api.dependencies.auth import get_current_principal, require_roles
from fourpro_api.repositories.audit_repository import AuditAction, AuditRepository
from fourpro_api.repositories.dashboard_repository import DashboardRepository
from fourpro_api.repositories.ingestion_repository import IngestionRepository

router = APIRouter(prefix="/dashboards", tags=["dashboards"])


def _widget_out(w, *, dataset_ok: bool) -> DashboardWidgetOut:
    return DashboardWidgetOut(
        id=str(w.id),
        widget_type=w.widget_type,  # type: ignore[arg-type]
        title=w.title,
        dataset_id=str(w.dataset_id) if w.dataset_id else None,
        config=w.config or {},
        position=w.position or {},
        dataset_available=dataset_ok,
    )


def _detail(dash, ing_repo: IngestionRepository) -> DashboardDetail:
    widgets = []
    for w in sorted(dash.widgets, key=lambda x: x.sort_order):
        ok = True
        if w.dataset_id:
            ds = ing_repo.get(w.dataset_id, dash.tenant_id)
            ok = ds is not None and ds.status == "processed"
        widgets.append(_widget_out(w, dataset_ok=ok))
    return DashboardDetail(
        id=str(dash.id),
        tenant_id=str(dash.tenant_id),
        title=dash.title,
        description=dash.description,
        updated_at=dash.updated_at.isoformat(),
        widget_count=len(widgets),
        layout_json=dash.layout_json or {},
        widgets=widgets,
        created_at=dash.created_at.isoformat(),
        created_by_user_id=str(dash.created_by_user_id) if dash.created_by_user_id else None,
    )


def _widget_dicts(widgets) -> list[dict[str, Any]]:
    return [
        {
            "widget_type": w.widget_type,
            "title": w.title,
            "dataset_id": w.dataset_id,
            "config": w.config,
            "position": w.position,
        }
        for w in widgets
    ]


@router.get("", response_model=PaginatedDashboardList)
def list_dashboards(
    principal: Annotated[Principal, Depends(get_current_principal)],
    db: Annotated[Session, Depends(get_db)],
    limit: int = 50,
    offset: int = 0,
) -> PaginatedDashboardList:
    repo = DashboardRepository(db)
    rows, total = repo.list_page(principal.tenant_id, limit=min(limit, 200), offset=max(offset, 0))
    items = [
        DashboardSummary(
            id=str(r.id),
            tenant_id=str(r.tenant_id),
            title=r.title,
            description=r.description,
            updated_at=r.updated_at.isoformat(),
            widget_count=len(r.widgets),
        )
        for r in rows
    ]
    return PaginatedDashboardList(items=items, total=total, limit=limit, offset=offset)


@router.post("", response_model=DashboardDetail, status_code=status.HTTP_201_CREATED)
def create_dashboard(
    body: DashboardCreate,
    principal: Annotated[Principal, Depends(require_roles("admin", "analyst"))],
    db: Annotated[Session, Depends(get_db)],
) -> DashboardDetail:
    repo = DashboardRepository(db)
    dash = repo.create(
        tenant_id=principal.tenant_id,
        title=body.title,
        description=body.description,
        layout_json=body.layout_json,
        created_by_user_id=principal.user_id,
        widgets=_widget_dicts(body.widgets),
    )
    AuditRepository(db).record(
        action=AuditAction.DASHBOARD_CREATED,
        actor_user_id=principal.user_id,
        tenant_id=principal.tenant_id,
        context={"dashboard_id": str(dash.id)},
    )
    return _detail(dash, IngestionRepository(db))


@router.get("/{dashboard_id}", response_model=DashboardDetail)
def get_dashboard(
    dashboard_id: UUID,
    principal: Annotated[Principal, Depends(get_current_principal)],
    db: Annotated[Session, Depends(get_db)],
) -> DashboardDetail:
    dash = DashboardRepository(db).get(dashboard_id, principal.tenant_id)
    if dash is None:
        raise HTTPException(status_code=404, detail="Dashboard não encontrado")
    return _detail(dash, IngestionRepository(db))


@router.patch("/{dashboard_id}", response_model=DashboardDetail)
def update_dashboard(
    dashboard_id: UUID,
    body: DashboardUpdate,
    principal: Annotated[Principal, Depends(require_roles("admin", "analyst"))],
    db: Annotated[Session, Depends(get_db)],
) -> DashboardDetail:
    repo = DashboardRepository(db)
    dash = repo.get(dashboard_id, principal.tenant_id)
    if dash is None:
        raise HTTPException(status_code=404, detail="Dashboard não encontrado")
    dash = repo.update_meta(
        dash,
        title=body.title,
        description=body.description,
        layout_json=body.layout_json,
    )
    if body.widgets is not None:
        dash = repo.replace_widgets(dash, _widget_dicts(body.widgets))
    AuditRepository(db).record(
        action=AuditAction.DASHBOARD_UPDATED,
        actor_user_id=principal.user_id,
        tenant_id=principal.tenant_id,
        context={"dashboard_id": str(dash.id)},
    )
    return _detail(dash, IngestionRepository(db))


@router.delete("/{dashboard_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_dashboard(
    dashboard_id: UUID,
    principal: Annotated[Principal, Depends(require_roles("admin", "analyst"))],
    db: Annotated[Session, Depends(get_db)],
) -> None:
    repo = DashboardRepository(db)
    dash = repo.get(dashboard_id, principal.tenant_id)
    if dash is None:
        raise HTTPException(status_code=404, detail="Dashboard não encontrado")
    repo.delete(dash)
    AuditRepository(db).record(
        action=AuditAction.DASHBOARD_DELETED,
        actor_user_id=principal.user_id,
        tenant_id=principal.tenant_id,
        context={"dashboard_id": str(dashboard_id)},
    )


@router.get("/{dashboard_id}/export", response_model=DashboardExportPackage)
def export_dashboard(
    dashboard_id: UUID,
    principal: Annotated[Principal, Depends(get_current_principal)],
    db: Annotated[Session, Depends(get_db)],
) -> DashboardExportPackage:
    dash = DashboardRepository(db).get(dashboard_id, principal.tenant_id)
    if dash is None:
        raise HTTPException(status_code=404, detail="Dashboard não encontrado")
    return DashboardExportPackage(
        dashboard=_detail(dash, IngestionRepository(db)),
        exported_at=datetime.now(tz=UTC).isoformat(),
    )
