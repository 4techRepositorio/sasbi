from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from fourpro_contracts.dataset import DatasetItem, PaginatedDatasetList
from fourpro_contracts.governance import PromoteDatasetRequest, PromoteDatasetResponse
from sqlalchemy.orm import Session

from fourpro_api.core.principal import Principal
from fourpro_api.db.session import get_db
from fourpro_api.dependencies.auth import get_current_principal, require_roles
from fourpro_api.repositories.ingestion_repository import IngestionRepository
from fourpro_api.services.governance_service import GovernanceService

router = APIRouter(prefix="/datasets", tags=["datasets"])


def _item(r) -> DatasetItem:
    return DatasetItem(
        id=str(r.id),
        tenant_id=str(r.tenant_id),
        original_filename=r.original_filename,
        status=r.status,
        size_bytes=r.size_bytes,
        result_summary=r.result_summary,
        created_at=r.created_at.isoformat(),
        layer=getattr(r, "layer", None) or "bronze",
        source_ingestion_id=str(r.source_ingestion_id) if r.source_ingestion_id else None,
        transform_version=r.transform_version,
    )


@router.get("", summary="Catálogo de datasets processados (TICKET-009/012)")
def list_datasets(
    principal: Annotated[Principal, Depends(get_current_principal)],
    db: Annotated[Session, Depends(get_db)],
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    layer: Literal["bronze", "silver", "gold"] | None = Query(default=None),
) -> PaginatedDatasetList:
    repo = IngestionRepository(db)
    rows, total = repo.list_processed_page(
        principal.tenant_id, limit=limit, offset=offset, layer=layer
    )
    return PaginatedDatasetList(
        items=[_item(r) for r in rows], total=total, limit=limit, offset=offset
    )


@router.post(
    "/{dataset_id}/promote",
    summary="Promover dataset para camada superior (TICKET-012)",
    response_model=PromoteDatasetResponse,
)
def promote_dataset(
    dataset_id: UUID,
    body: PromoteDatasetRequest,
    principal: Annotated[Principal, Depends(require_roles("admin", "analyst"))],
    db: Annotated[Session, Depends(get_db)],
) -> PromoteDatasetResponse:
    row = GovernanceService(db).promote(
        tenant_id=principal.tenant_id,
        actor_user_id=principal.user_id,
        source_id=dataset_id,
        target_layer=body.target_layer,
        transform_version=body.transform_version,
    )
    return PromoteDatasetResponse(
        id=str(row.id),
        tenant_id=str(row.tenant_id),
        source_ingestion_id=str(row.source_ingestion_id),
        layer=row.layer,  # type: ignore[arg-type]
        transform_version=row.transform_version or body.transform_version,
        status=row.status,
    )
