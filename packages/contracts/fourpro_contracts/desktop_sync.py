"""Contratos de publicação Desktop → API (TICKET-017)."""

from typing import Any, Literal

from pydantic import BaseModel, Field

from fourpro_contracts.dashboard import DashboardLayout


class DesktopPublishDatasetRequest(BaseModel):
    """Publica ou actualiza um dataset a partir de rascunho Desktop."""

    name: str = Field(min_length=1, max_length=200)
    data_source_id: str | None = None
    object_id: str | None = None
    semantic_fields: list[dict[str, Any]] = Field(default_factory=list)
    client_draft_id: str | None = None


class DesktopPublishDatasetResponse(BaseModel):
    dataset_id: str | None = None
    semantic_model_id: str | None = None
    sync_run_id: str | None = None
    status: Literal["queued", "processed", "failed"]
    message: str


class DesktopPublishDashboardRequest(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: str | None = None
    layout: DashboardLayout
    client_draft_id: str | None = None
    publish: bool = True


class DesktopPublishDashboardResponse(BaseModel):
    dashboard_id: str
    version: int
    status: Literal["draft", "published"]
    message: str


class DesktopSessionInfo(BaseModel):
    """Metadados úteis ao cliente Desktop após login."""

    user_id: str
    tenant_id: str
    tenant_name: str
    role: str
    api_base_url: str
    features: list[str] = Field(default_factory=list)
