"""Publicação Desktop → API (TICKET-017 endpoints)."""

from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException, status
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
from fourpro_api.services.dashboard_service import DashboardService


class DesktopSyncService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._dashboards = DashboardService(db)

    def session_info(self, principal: Principal) -> DesktopSessionInfo:
        tenant = self._db.get(Tenant, principal.tenant_id)
        if tenant is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tenant não encontrado",
            )
        settings = get_settings()
        api_base = settings.app_public_url.rstrip("/")
        # Prefer API path; clients may override via config
        if not api_base.endswith("/api/v1"):
            # APP_PUBLIC_URL is typically the front; expose documented API base as relative hint
            api_base_url = "/api/v1"
        else:
            api_base_url = api_base
        return DesktopSessionInfo(
            user_id=str(principal.user_id),
            tenant_id=str(principal.tenant_id),
            tenant_name=tenant.name,
            role=principal.role,
            api_base_url=api_base_url,
            features=["semantic-query", "dashboards", "file-upload"],
        )

    def publish_dataset(
        self,
        principal: Principal,
        body: DesktopPublishDatasetRequest,
    ) -> DesktopPublishDatasetResponse:
        """Sem data sources (TICKET-015) ainda — resposta explícita, sem inventar sync."""
        _ = principal
        if not body.data_source_id:
            return DesktopPublishDatasetResponse(
                dataset_id=None,
                semantic_model_id=None,
                sync_run_id=None,
                status="failed",
                message=(
                    "Publicação de dataset a partir do Desktop requer uma fonte de dados "
                    "(data_source_id). O módulo de conectores ainda não está disponível; "
                    "use upload de ficheiro + modelo semântico na API Web."
                ),
            )
        return DesktopPublishDatasetResponse(
            dataset_id=None,
            semantic_model_id=None,
            sync_run_id=None,
            status="failed",
            message=(
                f"Fonte de dados {body.data_source_id} não encontrada ou sync não configurado. "
                "Enqueue de sync será activado quando o catálogo de conectores estiver disponível."
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
