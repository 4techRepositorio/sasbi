"""CRUD e operações de fontes de dados (TICKET-015)."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from fourpro_contracts.connectors import (
    ConnectionTestResult,
    DataSourceCreate,
    DataSourceItem,
    DataSourcePatch,
    DiscoverResponse,
    PaginatedDataSourceList,
    PaginatedSyncRunList,
    SampleSchemaResponse,
    SyncEnqueuedResponse,
    SyncRequest,
)
from sqlalchemy.orm import Session

from fourpro_api.core.principal import Principal
from fourpro_api.db.session import get_db
from fourpro_api.dependencies.auth import get_current_principal, require_roles
from fourpro_api.services.data_source_service import DataSourceService

router = APIRouter(prefix="/data-sources", tags=["data-sources"])


@router.get("", summary="Listar fontes de dados do tenant")
def list_data_sources(
    principal: Annotated[Principal, Depends(get_current_principal)],
    db: Annotated[Session, Depends(get_db)],
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> PaginatedDataSourceList:
    return DataSourceService(db).list_sources(principal, limit=limit, offset=offset)


@router.post(
    "",
    summary="Criar fonte de dados",
    status_code=status.HTTP_201_CREATED,
    response_model=DataSourceItem,
)
def create_data_source(
    body: DataSourceCreate,
    principal: Annotated[Principal, Depends(require_roles("admin", "analyst"))],
    db: Annotated[Session, Depends(get_db)],
) -> DataSourceItem:
    return DataSourceService(db).create(principal, body)


@router.get("/{data_source_id}", summary="Detalhe da fonte (sem secrets)")
def get_data_source(
    data_source_id: UUID,
    principal: Annotated[Principal, Depends(get_current_principal)],
    db: Annotated[Session, Depends(get_db)],
) -> DataSourceItem:
    return DataSourceService(db).get(principal, data_source_id)


@router.patch("/{data_source_id}", summary="Actualizar fonte")
def patch_data_source(
    data_source_id: UUID,
    body: DataSourcePatch,
    principal: Annotated[Principal, Depends(require_roles("admin", "analyst"))],
    db: Annotated[Session, Depends(get_db)],
) -> DataSourceItem:
    return DataSourceService(db).patch(principal, data_source_id, body)


@router.delete(
    "/{data_source_id}",
    summary="Eliminar fonte",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_data_source(
    data_source_id: UUID,
    principal: Annotated[Principal, Depends(require_roles("admin", "analyst"))],
    db: Annotated[Session, Depends(get_db)],
) -> None:
    DataSourceService(db).delete(principal, data_source_id)


@router.post("/{data_source_id}/test", summary="Testar ligação")
def test_data_source(
    data_source_id: UUID,
    principal: Annotated[Principal, Depends(require_roles("admin", "analyst"))],
    db: Annotated[Session, Depends(get_db)],
) -> ConnectionTestResult:
    return DataSourceService(db).test_connection(principal, data_source_id)


@router.post("/{data_source_id}/discover", summary="Descobrir objectos")
def discover_data_source(
    data_source_id: UUID,
    principal: Annotated[Principal, Depends(require_roles("admin", "analyst"))],
    db: Annotated[Session, Depends(get_db)],
) -> DiscoverResponse:
    return DataSourceService(db).discover(principal, data_source_id)


@router.post("/{data_source_id}/sample-schema", summary="Amostrar schema")
def sample_schema_data_source(
    data_source_id: UUID,
    principal: Annotated[Principal, Depends(require_roles("admin", "analyst"))],
    db: Annotated[Session, Depends(get_db)],
    object_id: str = Query(..., min_length=1),
    limit: int = Query(default=100, ge=1, le=500),
) -> SampleSchemaResponse:
    return DataSourceService(db).sample_schema(
        principal, data_source_id, object_id=object_id, limit=limit
    )


@router.post("/{data_source_id}/sync", summary="Enfileirar sincronização")
def sync_data_source(
    data_source_id: UUID,
    body: SyncRequest,
    principal: Annotated[Principal, Depends(require_roles("admin", "analyst"))],
    db: Annotated[Session, Depends(get_db)],
) -> SyncEnqueuedResponse:
    return DataSourceService(db).enqueue_sync(principal, data_source_id, body)


@router.get("/{data_source_id}/sync-runs", summary="Histórico de syncs")
def list_sync_runs(
    data_source_id: UUID,
    principal: Annotated[Principal, Depends(get_current_principal)],
    db: Annotated[Session, Depends(get_db)],
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> PaginatedSyncRunList:
    return DataSourceService(db).list_sync_runs(
        principal, data_source_id, limit=limit, offset=offset
    )
