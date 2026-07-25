from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response, status
from fourpro_contracts.dashboard import (
    DashboardCreate,
    DashboardItem,
    DashboardPatch,
    DashboardPublishResponse,
    PaginatedDashboardList,
)
from sqlalchemy.orm import Session

from fourpro_api.core.principal import Principal
from fourpro_api.db.session import get_db
from fourpro_api.dependencies.auth import get_current_principal, require_roles
from fourpro_api.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboards", tags=["dashboards"])


def _svc(db: Annotated[Session, Depends(get_db)]) -> DashboardService:
    return DashboardService(db)


@router.get("", summary="Listar dashboards do tenant (TICKET-011)")
def list_dashboards(
    principal: Annotated[Principal, Depends(get_current_principal)],
    svc: Annotated[DashboardService, Depends(_svc)],
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    status_filter: str | None = Query(default=None, alias="status"),
) -> PaginatedDashboardList:
    return svc.list(
        principal.tenant_id,
        limit=limit,
        offset=offset,
        status_filter=status_filter,
    )


@router.post("", summary="Criar dashboard", status_code=status.HTTP_201_CREATED)
def create_dashboard(
    body: DashboardCreate,
    principal: Annotated[Principal, Depends(require_roles("admin", "analyst"))],
    svc: Annotated[DashboardService, Depends(_svc)],
) -> DashboardItem:
    return svc.create(principal.tenant_id, principal.user_id, body)


@router.get("/{dashboard_id}", summary="Detalhe de dashboard")
def get_dashboard(
    dashboard_id: UUID,
    principal: Annotated[Principal, Depends(get_current_principal)],
    svc: Annotated[DashboardService, Depends(_svc)],
) -> DashboardItem:
    return svc.get(principal.tenant_id, dashboard_id)


@router.patch("/{dashboard_id}", summary="Actualizar dashboard")
def patch_dashboard(
    dashboard_id: UUID,
    body: DashboardPatch,
    principal: Annotated[Principal, Depends(require_roles("admin", "analyst"))],
    svc: Annotated[DashboardService, Depends(_svc)],
) -> DashboardItem:
    return svc.patch(principal.tenant_id, dashboard_id, body)


@router.delete(
    "/{dashboard_id}",
    summary="Eliminar dashboard",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
def delete_dashboard(
    dashboard_id: UUID,
    principal: Annotated[Principal, Depends(require_roles("admin", "analyst"))],
    svc: Annotated[DashboardService, Depends(_svc)],
) -> Response:
    svc.delete(principal.tenant_id, dashboard_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{dashboard_id}/publish", summary="Publicar dashboard (snapshot de versão)")
def publish_dashboard(
    dashboard_id: UUID,
    principal: Annotated[Principal, Depends(require_roles("admin", "analyst"))],
    svc: Annotated[DashboardService, Depends(_svc)],
) -> DashboardPublishResponse:
    return svc.publish(principal.tenant_id, dashboard_id)
