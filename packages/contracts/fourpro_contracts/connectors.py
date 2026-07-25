"""Contratos de conectores / fontes de dados (TICKET-015)."""

from typing import Any, Literal

from pydantic import BaseModel, Field

ConnectorType = Literal[
    "file",
    "postgres",
    "mysql",
    "sqlserver",
    "rest_json",
    "s3_compatible",
]

DataSourceStatus = Literal["ready", "syncing", "error", "disabled"]

SyncRunStatus = Literal[
    "queued",
    "running",
    "uploaded",
    "validating",
    "parsing",
    "processed",
    "failed",
]

AuthKind = Literal["none", "password", "token", "api_key", "aws_sig_v4"]


class ConnectorCapability(BaseModel):
    connector_type: ConnectorType
    display_name: str
    description: str
    auth_kinds: list[AuthKind]
    supports_incremental: bool = False
    supports_discover: bool = True
    max_sample_rows: int = 100
    config_schema_hint: dict[str, Any] = Field(default_factory=dict)


class ConnectorCatalogResponse(BaseModel):
    items: list[ConnectorCapability]


class DataSourceCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    connector_type: ConnectorType
    config: dict[str, Any] = Field(default_factory=dict)
    """Configuração sem segredos (host, database, path, url base, etc.)."""
    secret: dict[str, str] | None = None
    """Credenciais (password, token, api_key, …) — nunca devolvidas em GET."""


class DataSourcePatch(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    config: dict[str, Any] | None = None
    secret: dict[str, str] | None = None
    status: Literal["ready", "disabled"] | None = None


class DataSourceItem(BaseModel):
    id: str
    tenant_id: str
    name: str
    connector_type: ConnectorType
    config: dict[str, Any]
    status: DataSourceStatus
    has_secret: bool
    last_sync_at: str | None = None
    last_error: str | None = None
    created_by_user_id: str | None = None
    created_at: str
    updated_at: str


class PaginatedDataSourceList(BaseModel):
    items: list[DataSourceItem]
    total: int
    limit: int
    offset: int


class ConnectionTestResult(BaseModel):
    ok: bool
    message: str
    details: dict[str, Any] = Field(default_factory=dict)


class DiscoverObject(BaseModel):
    object_id: str
    name: str
    kind: str = "table"
    meta: dict[str, Any] = Field(default_factory=dict)


class DiscoverResponse(BaseModel):
    objects: list[DiscoverObject]


class SchemaColumn(BaseModel):
    name: str
    inferred_type: str
    nullable: bool = True


class SampleSchemaResponse(BaseModel):
    object_id: str
    columns: list[SchemaColumn]
    sample_rows: list[dict[str, Any]] = Field(default_factory=list)


class SyncRequest(BaseModel):
    object_id: str | None = None
    """Objecto a extrair (tabela, path, endpoint). Opcional se a config já fixar."""
    mode: Literal["full", "sample"] = "full"
    sample_limit: int = Field(default=10_000, ge=1, le=1_000_000)


class SyncRunItem(BaseModel):
    id: str
    tenant_id: str
    data_source_id: str
    ingestion_id: str | None = None
    status: SyncRunStatus
    object_id: str | None = None
    friendly_message: str | None = None
    technical_log: str | None = None
    started_at: str | None = None
    finished_at: str | None = None
    created_at: str


class PaginatedSyncRunList(BaseModel):
    items: list[SyncRunItem]
    total: int
    limit: int
    offset: int


class SyncEnqueuedResponse(BaseModel):
    sync_run_id: str
    status: SyncRunStatus = "queued"
    message: str = "Sincronização enfileirada."
