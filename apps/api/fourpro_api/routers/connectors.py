from __future__ import annotations

from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fourpro_connectors import get_connector, list_connector_types
from fourpro_connectors.spi import ConnectorContext
from fourpro_contracts.connectors import (
    ConnectionTestResponse,
    ConnectorCapability,
    ConnectorCatalogResponse,
    DataSourceCreate,
    DataSourceItem,
    DataSourceUpdate,
    PaginatedDataSourceList,
    SyncEnqueueResponse,
    SyncRunItem,
)
from sqlalchemy.orm import Session

from fourpro_api.core.principal import Principal
from fourpro_api.db.session import get_db
from fourpro_api.dependencies.auth import get_current_principal, require_roles
from fourpro_api.middleware.correlation import get_correlation_id
from fourpro_api.repositories.audit_repository import AuditAction, AuditRepository
from fourpro_api.repositories.data_source_repository import DataSourceRepository
from fourpro_api.tasks_dispatch import enqueue_data_source_sync

router = APIRouter(tags=["connectors"])


def _item(src, *, has_secret: bool) -> DataSourceItem:
    return DataSourceItem(
        id=str(src.id),
        tenant_id=str(src.tenant_id),
        name=src.name,
        connector_type=src.connector_type,  # type: ignore[arg-type]
        config=src.config_json or {},
        status=src.status,  # type: ignore[arg-type]
        has_secret=has_secret,
        created_at=src.created_at.isoformat(),
        updated_at=src.updated_at.isoformat(),
    )


@router.get("/connectors", response_model=ConnectorCatalogResponse)
def list_connectors(
    _: Annotated[Principal, Depends(get_current_principal)],
) -> ConnectorCatalogResponse:
    items = []
    for c in list_connector_types():
        schema: dict[str, Any] = {}
        if c.type == "postgres":
            schema = {
                "host": "string",
                "port": "number",
                "database": "string",
                "table": "string",
                "limit": "number",
            }
        elif c.type == "rest_json":
            schema = {"url": "string", "allowlist_hosts": "string[]"}
        elif c.type == "file":
            schema = {"path": "string (opcional)"}
        items.append(
            ConnectorCapability(
                type=c.type,  # type: ignore[arg-type]
                display_name=c.display_name,
                supports_test=True,
                supports_sync=True,
                config_schema=schema,
            )
        )
    return ConnectorCatalogResponse(items=items)


@router.get("/data-sources", response_model=PaginatedDataSourceList)
def list_sources(
    principal: Annotated[Principal, Depends(get_current_principal)],
    db: Annotated[Session, Depends(get_db)],
    limit: int = 50,
    offset: int = 0,
) -> PaginatedDataSourceList:
    repo = DataSourceRepository(db)
    rows, total = repo.list_page(principal.tenant_id, limit=min(limit, 200), offset=max(offset, 0))
    items = [_item(r, has_secret=repo.has_secret(r.id)) for r in rows]
    return PaginatedDataSourceList(items=items, total=total, limit=limit, offset=offset)


@router.post("/data-sources", response_model=DataSourceItem, status_code=status.HTTP_201_CREATED)
def create_source(
    body: DataSourceCreate,
    principal: Annotated[Principal, Depends(require_roles("admin", "analyst"))],
    db: Annotated[Session, Depends(get_db)],
) -> DataSourceItem:
    if get_connector(body.connector_type) is None:
        raise HTTPException(status_code=400, detail="Tipo de conector inválido")
    repo = DataSourceRepository(db)
    src = repo.create(
        tenant_id=principal.tenant_id,
        name=body.name,
        connector_type=body.connector_type,
        config=body.config,
        created_by_user_id=principal.user_id,
        secret=body.secret,
    )
    AuditRepository(db).record(
        action=AuditAction.DATA_SOURCE_CREATED,
        actor_user_id=principal.user_id,
        tenant_id=principal.tenant_id,
        context={"data_source_id": str(src.id), "connector_type": src.connector_type},
    )
    return _item(src, has_secret=bool(body.secret))


@router.get("/data-sources/{source_id}", response_model=DataSourceItem)
def get_source(
    source_id: UUID,
    principal: Annotated[Principal, Depends(get_current_principal)],
    db: Annotated[Session, Depends(get_db)],
) -> DataSourceItem:
    repo = DataSourceRepository(db)
    src = repo.get(source_id, principal.tenant_id)
    if src is None:
        raise HTTPException(status_code=404, detail="Fonte não encontrada")
    return _item(src, has_secret=repo.has_secret(src.id))


@router.patch("/data-sources/{source_id}", response_model=DataSourceItem)
def patch_source(
    source_id: UUID,
    body: DataSourceUpdate,
    principal: Annotated[Principal, Depends(require_roles("admin", "analyst"))],
    db: Annotated[Session, Depends(get_db)],
) -> DataSourceItem:
    repo = DataSourceRepository(db)
    src = repo.get(source_id, principal.tenant_id)
    if src is None:
        raise HTTPException(status_code=404, detail="Fonte não encontrada")
    src = repo.update(
        src,
        name=body.name,
        config=body.config,
        status=body.status,
        secret=body.secret,
    )
    return _item(src, has_secret=repo.has_secret(src.id))


@router.delete("/data-sources/{source_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_source(
    source_id: UUID,
    principal: Annotated[Principal, Depends(require_roles("admin", "analyst"))],
    db: Annotated[Session, Depends(get_db)],
) -> None:
    repo = DataSourceRepository(db)
    src = repo.get(source_id, principal.tenant_id)
    if src is None:
        raise HTTPException(status_code=404, detail="Fonte não encontrada")
    repo.delete(src)


@router.post("/data-sources/{source_id}/test", response_model=ConnectionTestResponse)
def test_source(
    source_id: UUID,
    principal: Annotated[Principal, Depends(require_roles("admin", "analyst"))],
    db: Annotated[Session, Depends(get_db)],
) -> ConnectionTestResponse:
    repo = DataSourceRepository(db)
    src = repo.get(source_id, principal.tenant_id)
    if src is None:
        raise HTTPException(status_code=404, detail="Fonte não encontrada")
    connector = get_connector(src.connector_type)
    if connector is None:
        raise HTTPException(status_code=400, detail="Tipo de conector inválido")
    secret = repo.get_secret(src.id, src.tenant_id)
    result = connector.test_connection(
        ConnectorContext(
            tenant_id=str(src.tenant_id),
            data_source_id=str(src.id),
            config=dict(src.config_json or {}),
            secret=secret,
            correlation_id=get_correlation_id(),
        )
    )
    AuditRepository(db).record(
        action=AuditAction.DATA_SOURCE_TESTED,
        actor_user_id=principal.user_id,
        tenant_id=principal.tenant_id,
        context={"data_source_id": str(src.id), "ok": result.ok},
    )
    return ConnectionTestResponse(ok=result.ok, message=result.message)


@router.post("/data-sources/{source_id}/sync", response_model=SyncEnqueueResponse)
def sync_source(
    source_id: UUID,
    principal: Annotated[Principal, Depends(require_roles("admin", "analyst"))],
    db: Annotated[Session, Depends(get_db)],
) -> SyncEnqueueResponse:
    repo = DataSourceRepository(db)
    src = repo.get(source_id, principal.tenant_id)
    if src is None:
        raise HTTPException(status_code=404, detail="Fonte não encontrada")
    cid = get_correlation_id()
    run = repo.create_sync_run(
        tenant_id=principal.tenant_id,
        data_source_id=src.id,
        correlation_id=cid,
    )
    AuditRepository(db).record(
        action=AuditAction.DATA_SOURCE_SYNC_ENQUEUED,
        actor_user_id=principal.user_id,
        tenant_id=principal.tenant_id,
        context={"data_source_id": str(src.id), "sync_run_id": str(run.id)},
    )
    enqueue_data_source_sync(str(run.id), correlation_id=cid, db=db)
    # Re-ler após fallback síncrono
    run = repo.get_sync_run(run.id) or run
    return SyncEnqueueResponse(
        sync_run_id=str(run.id),
        status=run.status,  # type: ignore[arg-type]
        ingestion_id=str(run.ingestion_id) if run.ingestion_id else None,
    )


@router.get("/data-sources/{source_id}/sync-runs", response_model=list[SyncRunItem])
def list_sync_runs(
    source_id: UUID,
    principal: Annotated[Principal, Depends(get_current_principal)],
    db: Annotated[Session, Depends(get_db)],
) -> list[SyncRunItem]:
    repo = DataSourceRepository(db)
    src = repo.get(source_id, principal.tenant_id)
    if src is None:
        raise HTTPException(status_code=404, detail="Fonte não encontrada")
    rows = repo.list_sync_runs(src.id, principal.tenant_id)
    return [
        SyncRunItem(
            id=str(r.id),
            data_source_id=str(r.data_source_id),
            status=r.status,  # type: ignore[arg-type]
            ingestion_id=str(r.ingestion_id) if r.ingestion_id else None,
            friendly_error=r.friendly_error,
            created_at=r.created_at.isoformat(),
            updated_at=r.updated_at.isoformat(),
        )
        for r in rows
    ]
