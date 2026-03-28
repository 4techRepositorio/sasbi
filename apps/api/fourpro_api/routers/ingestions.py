from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fourpro_contracts.ingestion import IngestionItem
from sqlalchemy.orm import Session

from fourpro_api.core.principal import Principal
from fourpro_api.db.session import get_db
from fourpro_api.dependencies.auth import get_current_principal, require_roles
from fourpro_api.models.ingestion import FileIngestion
from fourpro_api.repositories.ingestion_repository import IngestionRepository
from fourpro_api.tasks_dispatch import enqueue_ingestion_parse

router = APIRouter(prefix="/ingestions", tags=["ingestions"])

_INGESTION_STATUSES = frozenset({"uploaded", "validating", "parsing", "processed", "failed"})


def _to_item(r: FileIngestion) -> IngestionItem:
    return IngestionItem(
        id=str(r.id),
        tenant_id=str(r.tenant_id),
        original_filename=r.original_filename,
        status=r.status,
        size_bytes=r.size_bytes,
        content_type=r.content_type,
        content_sha256=r.content_sha256,
        uploaded_by_user_id=str(r.uploaded_by_user_id) if r.uploaded_by_user_id else None,
        friendly_error=r.friendly_error,
        result_summary=r.result_summary,
        created_at=r.created_at.isoformat(),
    )


@router.get("", summary="Histórico de ingestões do tenant")
def list_ingestions(
    principal: Annotated[Principal, Depends(get_current_principal)],
    db: Annotated[Session, Depends(get_db)],
    status_filter: str | None = Query(default=None, alias="status"),
) -> list[IngestionItem]:
    if status_filter is not None and status_filter not in _INGESTION_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"status inválido; use um de: {sorted(_INGESTION_STATUSES)}",
        )
    repo = IngestionRepository(db)
    statuses = [status_filter] if status_filter else None
    rows = repo.list_for_tenant(principal.tenant_id, statuses=statuses)
    return [_to_item(r) for r in rows]


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
    return _to_item(row)


@router.post(
    "/{ingestion_id}/reprocess",
    summary="Reenfileirar ingestão (reprocessamento)",
)
def reprocess_ingestion(
    principal: Annotated[Principal, Depends(require_roles("admin", "analyst"))],
    db: Annotated[Session, Depends(get_db)],
    ingestion_id: UUID,
) -> IngestionItem:
    repo = IngestionRepository(db)
    row = repo.get(ingestion_id, principal.tenant_id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ingestão não encontrada")
    if row.status in ("validating", "parsing"):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ingestão em processamento; aguarde a conclusão antes de reprocessar",
        )
    repo.update(
        row,
        status="uploaded",
        friendly_error=None,
        technical_log=None,
        result_summary=None,
    )
    db.refresh(row)
    enqueue_ingestion_parse(str(row.id))
    db.refresh(row)
    return _to_item(row)
