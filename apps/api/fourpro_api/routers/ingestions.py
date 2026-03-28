from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from fourpro_contracts.ingestion import IngestionItem
from fourpro_api.core.principal import Principal
from fourpro_api.db.session import get_db
from fourpro_api.dependencies.auth import get_current_principal
from fourpro_api.repositories.ingestion_repository import IngestionRepository

router = APIRouter(prefix="/ingestions", tags=["ingestions"])


@router.get("", summary="Histórico de ingestões do tenant")
def list_ingestions(
    principal: Annotated[Principal, Depends(get_current_principal)],
    db: Annotated[Session, Depends(get_db)],
    status_filter: str | None = Query(default=None, alias="status"),
) -> list[IngestionItem]:
    repo = IngestionRepository(db)
    statuses = [status_filter] if status_filter else None
    rows = repo.list_for_tenant(principal.tenant_id, statuses=statuses)
    return [
        IngestionItem(
            id=str(r.id),
            tenant_id=str(r.tenant_id),
            original_filename=r.original_filename,
            status=r.status,
            size_bytes=r.size_bytes,
            friendly_error=r.friendly_error,
            result_summary=r.result_summary,
            created_at=r.created_at.isoformat(),
        )
        for r in rows
    ]


@router.get("/{ingestion_id}", summary="Detalhe de uma ingestão (TICKET-007)")
def get_ingestion(
    principal: Annotated[Principal, Depends(get_current_principal)],
    db: Annotated[Session, Depends(get_db)],
    ingestion_id: UUID,
) -> IngestionItem:
    repo = IngestionRepository(db)
    row = repo.get(ingestion_id, principal.tenant_id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ingestão não encontrada")
    return IngestionItem(
        id=str(row.id),
        tenant_id=str(row.tenant_id),
        original_filename=row.original_filename,
        status=row.status,
        size_bytes=row.size_bytes,
        friendly_error=row.friendly_error,
        result_summary=row.result_summary,
        created_at=row.created_at.isoformat(),
    )
