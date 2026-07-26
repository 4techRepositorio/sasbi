"""Contratos de conectores / fontes de dados (TICKET-015)."""

from typing import Any, Literal

from pydantic import BaseModel, Field

ConnectorType = Literal["file", "postgres", "rest_json"]
DataSourceStatus = Literal["active", "disabled", "error"]
SyncRunStatus = Literal["queued", "running", "processed", "failed"]


class ConnectorCapability(BaseModel):
    type: ConnectorType
    display_name: str
    supports_test: bool = True
    supports_sync: bool = True
    config_schema: dict[str, Any] = Field(default_factory=dict)


class ConnectorCatalogResponse(BaseModel):
    items: list[ConnectorCapability]


class DataSourceCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    connector_type: ConnectorType
    config: dict[str, Any] = Field(default_factory=dict)
    secret: str | None = Field(
        default=None,
        description="Credencial em texto claro só na criação/atualização; nunca devolvida.",
    )


class DataSourceUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    config: dict[str, Any] | None = None
    secret: str | None = None
    status: DataSourceStatus | None = None


class DataSourceItem(BaseModel):
    id: str
    tenant_id: str
    name: str
    connector_type: ConnectorType
    config: dict[str, Any]
    status: DataSourceStatus
    has_secret: bool
    created_at: str
    updated_at: str


class PaginatedDataSourceList(BaseModel):
    items: list[DataSourceItem]
    total: int
    limit: int
    offset: int


class ConnectionTestResponse(BaseModel):
    ok: bool
    message: str


class SyncEnqueueResponse(BaseModel):
    sync_run_id: str
    status: SyncRunStatus
    ingestion_id: str | None = None


class SyncRunItem(BaseModel):
    id: str
    data_source_id: str
    status: SyncRunStatus
    ingestion_id: str | None = None
    friendly_error: str | None = None
    created_at: str
    updated_at: str
