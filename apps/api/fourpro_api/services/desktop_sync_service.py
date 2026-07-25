"""Publicação Desktop → API (TICKET-017 endpoints)."""

from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException, status
from fourpro_contracts.connectors import SyncRequest
from fourpro_contracts.dashboard import DashboardCreate
from fourpro_contracts.desktop_sync import (
    DesktopPublishDashboardRequest,
    DesktopPublishDashboardResponse,
    DesktopPublishDatasetRequest,
    DesktopPublishDatasetResponse,
    DesktopSessionInfo,
)
from sqlalchemy.orm import Session

from fourpro_api.config import get_settings
from fourpro_api.core.principal import Principal
from fourpro_api.models.tenant import Tenant
from fourpro_api.repositories.data_source_repository import DataSourceRepository
from fourpro_api.services.dashboard_service import DashboardService
from fourpro_api.services.data_source_service import DataSourceService


class DesktopSyncService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._dashboards = DashboardService(db)
        self._data_sources = DataSourceService(db)
        self._ds_repo = DataSourceRepository(db)

    def session_info(self, principal: Principal) -> DesktopSessionInfo:
        tenant = self._db.get(Tenant, principal.tenant_id)
        if tenant is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tenant não encontrado",
            )
        settings = get_settings()
        api_base = settings.app_public_url.rstrip("/")
        if not api_base.endswith("/api/v1"):
            api_base_url = "/api/v1"
        else:
            api_base_url = api_base
        return DesktopSessionInfo(
            user_id=str(principal.user_id),
            tenant_id=str(principal.tenant_id),
            tenant_name=tenant.name,
            role=principal.role,
            api_base_url=api_base_url,
            features=[
                "connectors",
                "semantic-query",
                "dashboards",
                "file-upload",
                "desktop-publish",
            ],
        )

    def publish_dataset(
        self,
        principal: Principal,
        body: DesktopPublishDatasetRequest,
    ) -> DesktopPublishDatasetResponse:
        if not body.data_source_id:
            return DesktopPublishDatasetResponse(
                dataset_id=None,
                semantic_model_id=None,
                sync_run_id=None,
                status="failed",
                message=(
                    "Indique data_source_id da fonte configurada no Desktop "
                    "para enfileirar a sincronização."
                ),
            )
        try:
            ds_id = UUID(body.data_source_id)
        except ValueError:
            return DesktopPublishDatasetResponse(
                dataset_id=None,
                semantic_model_id=None,
                sync_run_id=None,
                status="failed",
                message="data_source_id inválido",
            )

        row = self._ds_repo.get_by_id(ds_id)
        if row is None or row.tenant_id != principal.tenant_id:
            return DesktopPublishDatasetResponse(
                dataset_id=None,
                semantic_model_id=None,
                sync_run_id=None,
                status="failed",
                message="Fonte de dados não encontrada neste tenant",
            )

        enqueued = self._data_sources.enqueue_sync(
            principal,
            ds_id,
            SyncRequest(object_id=body.object_id, mode="full"),
        )
        hint = ""
        if body.semantic_fields:
            hint = (
                " Campos semânticos recebidos: associe-os a um modelo após o dataset "
                "ficar processed (API Web ou Semantic Models)."
            )
        return DesktopPublishDatasetResponse(
            dataset_id=None,
            semantic_model_id=None,
            sync_run_id=enqueued.sync_run_id,
            status="queued",
            message=(
                f"Sincronização enfileirada para «{row.name}». "
                "Quando o status for processed, o dataset aparece no catálogo."
                f"{hint}"
            ),
        )

    def publish_dashboard(
        self,
        principal: Principal,
        body: DesktopPublishDashboardRequest,
    ) -> DesktopPublishDashboardResponse:
        created = self._dashboards.create(
            principal.tenant_id,
            principal.user_id,
            DashboardCreate(
                name=body.name,
                description=body.description,
                layout=body.layout,
            ),
        )
        dashboard_id = UUID(created.id)
        version = created.version
        status_out: str = "draft"
        message = "Dashboard criado como rascunho"
        if body.publish:
            pub = self._dashboards.publish(principal.tenant_id, dashboard_id)
            version = pub.version
            status_out = "published"
            message = "Dashboard publicado a partir do Desktop"
        return DesktopPublishDashboardResponse(
            dashboard_id=str(dashboard_id),
            version=version,
            status=status_out,  # type: ignore[arg-type]
            message=message,
        )
