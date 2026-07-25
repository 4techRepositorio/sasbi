"""Motor de query agregada sobre linhas tabulares (TICKET-016)."""

from __future__ import annotations

import logging
from collections import defaultdict
from pathlib import Path
from typing import Any
from uuid import UUID

from fastapi import HTTPException, status
from fourpro_contracts.semantic import (
    AggregationOp,
    QueryMeasure,
    QueryRequest,
    QueryResponse,
    SemanticField,
)
from sqlalchemy.orm import Session

from fourpro_api.models.ingestion import FileIngestion
from fourpro_api.repositories.ingestion_repository import IngestionRepository
from fourpro_api.repositories.semantic_repository import SemanticModelRepository
from fourpro_api.services.tabular_extract import extract_tabular_rows

logger = logging.getLogger(__name__)


def _to_number(value: Any) -> float | None:
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        return float(int(value))
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(str(value).replace(",", "").strip())
    except (TypeError, ValueError):
        return None


def _aggregate(op: AggregationOp, values: list[float], row_count: int) -> float | int | None:
    if op == "count":
        return row_count if not values else len(values)
    if not values:
        return None
    if op == "sum":
        return sum(values)
    if op == "avg":
        return sum(values) / len(values)
    if op == "min":
        return min(values)
    if op == "max":
        return max(values)
    # Exhaustive for AggregationOp Literal
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"Agregação não suportada: {op}",
    )


class QueryService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._semantic = SemanticModelRepository(db)
        self._ingestions = IngestionRepository(db)

    def execute(self, tenant_id: UUID, body: QueryRequest) -> QueryResponse:
        try:
            model_id = UUID(body.semantic_model_id)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="semantic_model_id inválido",
            ) from e

        model = self._semantic.get(model_id, tenant_id)
        if model is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Modelo semântico não encontrado",
            )

        dataset = self._ingestions.get(model.dataset_id, tenant_id)
        if dataset is None or dataset.status != "processed":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Dataset indisponível para consulta",
            )

        fields = [SemanticField.model_validate(f) for f in (model.fields_json or [])]
        by_name = {f.name: f for f in fields}
        if not by_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Modelo semântico sem campos definidos",
            )

        for dim in body.dimensions:
            if dim not in by_name:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Dimensão não permitida: {dim}",
                )
        for measure in body.measures:
            if measure.field not in by_name:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Medida não permitida: {measure.field}",
                )
        for key in body.filters:
            if key not in by_name:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Filtro não permitido: {key}",
                )

        rows = self._load_rows(dataset)
        projected = self._project_and_filter(rows, by_name, body.filters)
        result_rows = self._group_aggregate(
            projected,
            dimensions=body.dimensions,
            measures=body.measures,
        )
        truncated = len(result_rows) > body.limit
        limited = result_rows[: body.limit]
        columns: list[str] = list(body.dimensions)
        for m in body.measures:
            columns.append(m.alias or f"{m.op}_{m.field}")

        return QueryResponse(
            columns=columns,
            rows=limited,
            row_count=len(limited),
            truncated=truncated,
            semantic_model_id=str(model.id),
            dataset_id=str(dataset.id),
        )

    def _load_rows(self, dataset: FileIngestion) -> list[dict[str, Any]]:
        stored = dataset.parsed_rows_json
        if isinstance(stored, list) and stored:
            return stored

        path = Path(dataset.storage_path)
        if not path.exists():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Dados tabulares indisponíveis para este dataset",
            )
        try:
            rows, summary, _ = extract_tabular_rows(path)
        except Exception as e:
            logger.exception("query_fallback_parse_failed", extra={"dataset_id": str(dataset.id)})
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Não foi possível carregar dados para consulta",
            ) from e

        # Backfill para próximas queries
        self._ingestions.update(
            dataset,
            result_summary=dataset.result_summary or summary,
            parsed_rows_json=rows,
        )
        return rows

    def _project_and_filter(
        self,
        rows: list[dict[str, Any]],
        by_name: dict[str, SemanticField],
        filters: dict[str, Any],
    ) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        for raw in rows:
            projected: dict[str, Any] = {}
            for name, field in by_name.items():
                projected[name] = raw.get(field.source_column)
            ok = True
            for key, expected in filters.items():
                if projected.get(key) != expected:
                    ok = False
                    break
            if ok:
                out.append(projected)
        return out

    def _group_aggregate(
        self,
        rows: list[dict[str, Any]],
        *,
        dimensions: list[str],
        measures: list[QueryMeasure],
    ) -> list[dict[str, Any]]:
        groups: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
        for row in rows:
            key = tuple(row.get(d) for d in dimensions)
            groups[key].append(row)

        results: list[dict[str, Any]] = []
        for key, group_rows in groups.items():
            item: dict[str, Any] = {dimensions[i]: key[i] for i in range(len(dimensions))}
            for measure in measures:
                alias = measure.alias or f"{measure.op}_{measure.field}"
                if measure.op == "count":
                    item[alias] = sum(1 for r in group_rows if r.get(measure.field) is not None)
                    continue
                nums = [
                    n
                    for r in group_rows
                    if (n := _to_number(r.get(measure.field))) is not None
                ]
                item[alias] = _aggregate(measure.op, nums, len(group_rows))
            results.append(item)
        return results
