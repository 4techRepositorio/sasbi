from uuid import UUID

from fastapi import HTTPException, status
from fourpro_contracts.semantic import (
    PaginatedSemanticModelList,
    SemanticField,
    SemanticModelCreate,
    SemanticModelItem,
    SemanticModelPatch,
)
from sqlalchemy.orm import Session

from fourpro_api.models.semantic import SemanticModel
from fourpro_api.repositories.ingestion_repository import IngestionRepository
from fourpro_api.repositories.semantic_repository import SemanticModelRepository


def _to_item(row: SemanticModel) -> SemanticModelItem:
    fields = [SemanticField.model_validate(f) for f in (row.fields_json or [])]
    return SemanticModelItem(
        id=str(row.id),
        tenant_id=str(row.tenant_id),
        name=row.name,
        dataset_id=str(row.dataset_id),
        description=row.description,
        fields=fields,
        created_at=row.created_at.isoformat(),
        updated_at=row.updated_at.isoformat(),
    )


class SemanticModelService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._repo = SemanticModelRepository(db)
        self._ingestions = IngestionRepository(db)

    def create(self, tenant_id: UUID, body: SemanticModelCreate) -> SemanticModelItem:
        try:
            dataset_id = UUID(body.dataset_id)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="dataset_id inválido",
            ) from e
        dataset = self._ingestions.get(dataset_id, tenant_id)
        if dataset is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dataset não encontrado",
            )
        if dataset.status != "processed":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Dataset ainda não está processado",
            )
        fields_json = [f.model_dump() for f in body.fields]
        row = self._repo.create(
            tenant_id=tenant_id,
            name=body.name,
            dataset_id=dataset_id,
            description=body.description,
            fields_json=fields_json,
        )
        return _to_item(row)

    def get(self, tenant_id: UUID, model_id: UUID) -> SemanticModelItem:
        row = self._repo.get(model_id, tenant_id)
        if row is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Modelo semântico não encontrado",
            )
        return _to_item(row)

    def list(
        self,
        tenant_id: UUID,
        *,
        limit: int,
        offset: int,
    ) -> PaginatedSemanticModelList:
        rows, total = self._repo.list_page(tenant_id, limit=limit, offset=offset)
        return PaginatedSemanticModelList(
            items=[_to_item(r) for r in rows],
            total=total,
            limit=limit,
            offset=offset,
        )

    def patch(
        self,
        tenant_id: UUID,
        model_id: UUID,
        body: SemanticModelPatch,
    ) -> SemanticModelItem:
        row = self._repo.get(model_id, tenant_id)
        if row is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Modelo semântico não encontrado",
            )
        data = body.model_dump(exclude_unset=True)
        kwargs: dict = {}
        if "name" in data:
            kwargs["name"] = data["name"]
        if "description" in data:
            kwargs["description"] = data["description"]
        if "fields" in data:
            kwargs["fields_json"] = [
                SemanticField.model_validate(f).model_dump() for f in (data["fields"] or [])
            ]
        if kwargs:
            row = self._repo.update(row, **kwargs)
        return _to_item(row)

    def delete(self, tenant_id: UUID, model_id: UUID) -> None:
        row = self._repo.get(model_id, tenant_id)
        if row is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Modelo semântico não encontrado",
            )
        self._repo.delete(row)
