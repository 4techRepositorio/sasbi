from typing import Annotated

from fastapi import APIRouter, Depends
from fourpro_contracts.desktop_sync import (
    DesktopPublishDashboardRequest,
    DesktopPublishDashboardResponse,
    DesktopPublishDatasetRequest,
    DesktopPublishDatasetResponse,
    DesktopSessionInfo,
)
from sqlalchemy.orm import Session

from fourpro_api.core.principal import Principal
from fourpro_api.db.session import get_db
from fourpro_api.dependencies.auth import get_current_principal, require_roles
from fourpro_api.services.desktop_sync_service import DesktopSyncService

router = APIRouter(prefix="/desktop", tags=["desktop"])


def _svc(db: Annotated[Session, Depends(get_db)]) -> DesktopSyncService:
    return DesktopSyncService(db)


@router.get("/session", summary="Metadados de sessão para o cliente Desktop")
def desktop_session(
    principal: Annotated[Principal, Depends(get_current_principal)],
    svc: Annotated[DesktopSyncService, Depends(_svc)],
) -> DesktopSessionInfo:
    return svc.session_info(principal)


@router.post(
    "/publish-dataset",
    summary="Publicar dataset a partir do Desktop (requer conectores)",
)
def publish_dataset(
    body: DesktopPublishDatasetRequest,
    principal: Annotated[Principal, Depends(require_roles("admin", "analyst"))],
    svc: Annotated[DesktopSyncService, Depends(_svc)],
) -> DesktopPublishDatasetResponse:
    return svc.publish_dataset(principal, body)


@router.post(
    "/publish-dashboard",
    summary="Publicar dashboard a partir do Desktop",
)
def publish_dashboard(
    body: DesktopPublishDashboardRequest,
    principal: Annotated[Principal, Depends(require_roles("admin", "analyst"))],
    svc: Annotated[DesktopSyncService, Depends(_svc)],
) -> DesktopPublishDashboardResponse:
    return svc.publish_dashboard(principal, body)
