from typing import Annotated

from fastapi import APIRouter, Depends, Query
from fourpro_contracts.dataset import DatasetItem, PaginatedDatasetList
from sqlalchemy.orm import Session

from fourpro_api.core.principal import Principal
from fourpro_api.db.session import get_db
from fourpro_api.dependencies.auth import get_current_principal
from fourpro_api.repositories.ingestion_repository import IngestionRepository

router = APIRouter(prefix="/datasets", tags=["datasets"])


@router.get("", summary="Catálogo de datasets processados (TICKET-009)")
def list_datasets(
    principal: Annotated[Principal, Depends(get_current_principal)],
    db: Annotated[Session, Depends(get_db)],
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> PaginatedDatasetList:
    repo = IngestionRepository(db)
    rows, total = repo.list_processed_page(principal.tenant_id, limit=limit, offset=offset)
    items = [
        DatasetItem(
            id=str(r.id),
            tenant_id=str(r.tenant_id),
            original_filename=r.original_filename,
            status=r.status,
            size_bytes=r.size_bytes,
            result_summary=r.result_summary,
            created_at=r.created_at.isoformat(),
        )
        for r in rows
    ]
    return PaginatedDatasetList(items=items, total=total, limit=limit, offset=offset)
