from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from fourpro_api.models.semantic import SemanticModel


class SemanticRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def list_page(
        self, tenant_id: UUID, *, limit: int, offset: int
    ) -> tuple[list[SemanticModel], int]:
        filters = (SemanticModel.tenant_id == tenant_id,)
        total = int(
            self._db.scalar(select(func.count()).select_from(SemanticModel).where(*filters)) or 0
        )
        rows = list(
            self._db.scalars(
                select(SemanticModel)
                .where(*filters)
                .order_by(SemanticModel.updated_at.desc())
                .limit(limit)
                .offset(offset)
            ).all()
        )
        return rows, total

    def get(self, model_id: UUID, tenant_id: UUID) -> SemanticModel | None:
        row = self._db.get(SemanticModel, model_id)
        if row is None or row.tenant_id != tenant_id:
            return None
        return row

    def create(
        self,
        *,
        tenant_id: UUID,
        name: str,
        dataset_id: UUID,
        dimensions: list[dict[str, Any]],
        measures: list[dict[str, Any]],
        created_by_user_id: UUID | None,
    ) -> SemanticModel:
        now = datetime.now(tz=UTC)
        row = SemanticModel(
            tenant_id=tenant_id,
            name=name,
            dataset_id=dataset_id,
            dimensions_json=dimensions,
            measures_json=measures,
            created_by_user_id=created_by_user_id,
            created_at=now,
            updated_at=now,
        )
        self._db.add(row)
        self._db.commit()
        self._db.refresh(row)
        return row
