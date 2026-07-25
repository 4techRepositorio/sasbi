from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from fourpro_api.models.semantic import SemanticModel

_UNSET: Any = object()


class SemanticModelRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def create(
        self,
        *,
        tenant_id: UUID,
        name: str,
        dataset_id: UUID,
        description: str | None,
        fields_json: list[dict[str, Any]],
    ) -> SemanticModel:
        now = datetime.now(tz=UTC)
        row = SemanticModel(
            tenant_id=tenant_id,
            name=name,
            dataset_id=dataset_id,
            description=description,
            fields_json=fields_json,
            created_at=now,
            updated_at=now,
        )
        self._db.add(row)
        self._db.commit()
        self._db.refresh(row)
        return row

    def get(self, model_id: UUID, tenant_id: UUID) -> SemanticModel | None:
        row = self._db.get(SemanticModel, model_id)
        if row is None or row.tenant_id != tenant_id:
            return None
        return row

    def list_page(
        self,
        tenant_id: UUID,
        *,
        limit: int,
        offset: int,
    ) -> tuple[list[SemanticModel], int]:
        filters = (SemanticModel.tenant_id == tenant_id,)
        total = int(
            self._db.scalar(select(func.count()).select_from(SemanticModel).where(*filters)) or 0
        )
        stmt: Select[tuple[SemanticModel]] = (
            select(SemanticModel)
            .where(*filters)
            .order_by(SemanticModel.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(self._db.scalars(stmt).all()), total

    def update(
        self,
        row: SemanticModel,
        *,
        name: Any = _UNSET,
        description: Any = _UNSET,
        fields_json: Any = _UNSET,
    ) -> SemanticModel:
        if name is not _UNSET:
            row.name = name
        if description is not _UNSET:
            row.description = description
        if fields_json is not _UNSET:
            row.fields_json = fields_json
        row.updated_at = datetime.now(tz=UTC)
        self._db.add(row)
        self._db.commit()
        self._db.refresh(row)
        return row

    def delete(self, row: SemanticModel) -> None:
        self._db.delete(row)
        self._db.commit()
