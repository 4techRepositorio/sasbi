"""Endpoints de publicação Desktop → API (TICKET-017)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, status
from fourpro_contracts.desktop_sync import (
    DesktopPublishDashboardRequest,
    DesktopPublishDashboardResponse,
    DesktopPublishDatasetRequest,
    DesktopPublishDatasetResponse,
)
from sqlalchemy.orm import Session

from fourpro_api.config import get_settings
from fourpro_api.core.principal import Principal
from fourpro_api.db.session import get_db
from fourpro_api.dependencies.auth import require_roles
from fourpro_api.middleware.correlation import get_correlation_id
from fourpro_api.repositories.audit_repository import AuditAction, AuditRepository
from fourpro_api.repositories.dashboard_repository import DashboardRepository
from fourpro_api.repositories.ingestion_repository import IngestionRepository

router = APIRouter(prefix="/desktop", tags=["desktop"])


@router.post(
    "/publish/dataset",
    response_model=DesktopPublishDatasetResponse,
    status_code=status.HTTP_201_CREATED,
)
def publish_dataset(
    body: DesktopPublishDatasetRequest,
    principal: Annotated[Principal, Depends(require_roles("admin", "analyst"))],
    db: Annotated[Session, Depends(get_db)],
) -> DesktopPublishDatasetResponse:
    settings = get_settings()
    base = Path(settings.upload_dir) / str(principal.tenant_id) / "desktop"
    base.mkdir(parents=True, exist_ok=True)
    payload = json.dumps({"rows": body.rows}, ensure_ascii=False).encode("utf-8")
    dest = base / f"{uuid4()}_{body.title.replace(' ', '_')}.json"
    dest.write_bytes(payload)
    layer = body.layer if body.layer in ("bronze", "silver", "gold") else "gold"
    row = IngestionRepository(db).create(
        tenant_id=principal.tenant_id,
        original_filename=f"{body.title}.json",
        storage_path=str(dest.resolve()),
        content_type="application/json",
        size_bytes=len(payload),
        status="processed",
        uploaded_by_user_id=principal.user_id,
        layer=layer,
        correlation_id=get_correlation_id(),
        result_summary=f"Publicado pelo Desktop 4Pro_BI ({len(body.rows)} linhas)",
        technical_log="desktop.publish.dataset",
    )
    AuditRepository(db).record(
        action=AuditAction.DESKTOP_DATASET_PUBLISHED,
        actor_user_id=principal.user_id,
        tenant_id=principal.tenant_id,
        context={"dataset_id": str(row.id)},
    )
    return DesktopPublishDatasetResponse(
        dataset_id=str(row.id), status=row.status, layer=row.layer
    )


@router.post(
    "/publish/dashboard",
    response_model=DesktopPublishDashboardResponse,
    status_code=status.HTTP_201_CREATED,
)
def publish_dashboard(
    body: DesktopPublishDashboardRequest,
    principal: Annotated[Principal, Depends(require_roles("admin", "analyst"))],
    db: Annotated[Session, Depends(get_db)],
) -> DesktopPublishDashboardResponse:
    widgets = []
    for w in body.widgets:
        widgets.append(
            {
                "widget_type": w.get("widget_type", "kpi"),
                "title": w.get("title", "Widget"),
                "dataset_id": w.get("dataset_id"),
                "config": w.get("config") or {},
                "position": w.get("position") or {},
            }
        )
    dash = DashboardRepository(db).create(
        tenant_id=principal.tenant_id,
        title=body.title,
        description=body.description,
        layout_json=body.layout_json,
        created_by_user_id=principal.user_id,
        widgets=widgets,
    )
    AuditRepository(db).record(
        action=AuditAction.DESKTOP_DASHBOARD_PUBLISHED,
        actor_user_id=principal.user_id,
        tenant_id=principal.tenant_id,
        context={"dashboard_id": str(dash.id)},
    )
    return DesktopPublishDashboardResponse(dashboard_id=str(dash.id))
