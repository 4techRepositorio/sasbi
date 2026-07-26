from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fourpro_contracts.semantic import (
    PaginatedSemanticModelList,
    QueryRequest,
    QueryResponse,
    SemanticModelCreate,
    SemanticModelItem,
)
from sqlalchemy.orm import Session

from fourpro_api.core.principal import Principal
from fourpro_api.db.session import get_db
from fourpro_api.dependencies.auth import get_current_principal, require_roles
from fourpro_api.repositories.audit_repository import AuditAction, AuditRepository
from fourpro_api.repositories.ingestion_repository import IngestionRepository
from fourpro_api.repositories.semantic_repository import SemanticRepository

router = APIRouter(tags=["semantic"])


def _item(m) -> SemanticModelItem:
    return SemanticModelItem(
        id=str(m.id),
        tenant_id=str(m.tenant_id),
        name=m.name,
        dataset_id=str(m.dataset_id),
        dimensions=m.dimensions_json or [],
        measures=m.measures_json or [],
        updated_at=m.updated_at.isoformat(),
    )


@router.get("/semantic/models", response_model=PaginatedSemanticModelList)
def list_models(
    principal: Annotated[Principal, Depends(get_current_principal)],
    db: Annotated[Session, Depends(get_db)],
    limit: int = 50,
    offset: int = 0,
) -> PaginatedSemanticModelList:
    rows, total = SemanticRepository(db).list_page(
        principal.tenant_id, limit=min(limit, 200), offset=max(offset, 0)
    )
    return PaginatedSemanticModelList(
        items=[_item(r) for r in rows], total=total, limit=limit, offset=offset
    )


@router.post(
    "/semantic/models",
    response_model=SemanticModelItem,
    status_code=status.HTTP_201_CREATED,
)
def create_model(
    body: SemanticModelCreate,
    principal: Annotated[Principal, Depends(require_roles("admin", "analyst"))],
    db: Annotated[Session, Depends(get_db)],
) -> SemanticModelItem:
    ds = IngestionRepository(db).get(UUID(body.dataset_id), principal.tenant_id)
    if ds is None or ds.status != "processed":
        raise HTTPException(status_code=400, detail="Dataset processado inválido neste tenant")
    row = SemanticRepository(db).create(
        tenant_id=principal.tenant_id,
        name=body.name,
        dataset_id=ds.id,
        dimensions=[d.model_dump() for d in body.dimensions],
        measures=[m.model_dump() for m in body.measures],
        created_by_user_id=principal.user_id,
    )
    AuditRepository(db).record(
        action=AuditAction.SEMANTIC_MODEL_CREATED,
        actor_user_id=principal.user_id,
        tenant_id=principal.tenant_id,
        context={"semantic_model_id": str(row.id)},
    )
    return _item(row)


def _load_rows(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    raw = path.read_bytes()
    try:
        data = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        lines = raw.decode("utf-8", "replace").splitlines()[:200]
        return [{"line": i, "value": line} for i, line in enumerate(lines)]
    if isinstance(data, list):
        return [x for x in data if isinstance(x, dict)][:1000]
    if isinstance(data, dict):
        if isinstance(data.get("rows"), list):
            return [x for x in data["rows"] if isinstance(x, dict)][:1000]
        if isinstance(data.get("items"), list):
            return [x for x in data["items"] if isinstance(x, dict)][:1000]
        return [data]
    return []


@router.post("/query", response_model=QueryResponse)
def run_query(
    body: QueryRequest,
    principal: Annotated[Principal, Depends(get_current_principal)],
    db: Annotated[Session, Depends(get_db)],
) -> QueryResponse:
    model = SemanticRepository(db).get(UUID(body.semantic_model_id), principal.tenant_id)
    if model is None:
        raise HTTPException(status_code=404, detail="Modelo semântico não encontrado")
    ds = IngestionRepository(db).get(model.dataset_id, principal.tenant_id)
    if ds is None or ds.status != "processed":
        raise HTTPException(status_code=404, detail="Dataset do modelo indisponível")
    rows = _load_rows(Path(ds.storage_path))
    measure_defs = {m["name"]: m for m in (model.measures_json or [])}
    dim_defs = {d["name"]: d for d in (model.dimensions_json or [])}
    measures = body.measures or list(measure_defs.keys()) or ["count"]
    dimensions = [d for d in body.dimensions if d in dim_defs]

    if not dimensions:
        # Agregado global
        out_cols = measures
        values: list[Any] = []
        for mname in measures:
            mdef = measure_defs.get(mname) or {"expression": "count"}
            expr = mdef.get("expression", "count")
            field = mdef.get("field")
            if expr == "count":
                values.append(len(rows))
            elif expr in ("sum", "avg") and field:
                nums = [float(r[field]) for r in rows if field in r and _is_number(r[field])]
                if not nums:
                    values.append(0)
                elif expr == "sum":
                    values.append(sum(nums))
                else:
                    values.append(sum(nums) / len(nums))
            else:
                values.append(len(rows))
        return QueryResponse(
            columns=out_cols,
            rows=[values],
            dataset_id=str(ds.id),
            layer=ds.layer,
        )

    # Group by primeira dimensão (MVP)
    dim = dimensions[0]
    field = dim_defs[dim]["field"]
    groups: dict[Any, list[dict[str, Any]]] = {}
    for r in rows:
        key = r.get(field)
        groups.setdefault(key, []).append(r)
    out_rows: list[list[Any]] = []
    for key, group in list(groups.items())[: body.limit]:
        line: list[Any] = [key]
        for mname in measures:
            mdef = measure_defs.get(mname) or {"expression": "count"}
            expr = mdef.get("expression", "count")
            mfield = mdef.get("field")
            if expr == "count":
                line.append(len(group))
            elif expr in ("sum", "avg") and mfield:
                nums = [float(r[mfield]) for r in group if mfield in r and _is_number(r[mfield])]
                if not nums:
                    line.append(0)
                elif expr == "sum":
                    line.append(sum(nums))
                else:
                    line.append(sum(nums) / len(nums))
            else:
                line.append(len(group))
        out_rows.append(line)
    return QueryResponse(
        columns=[dim, *measures],
        rows=out_rows,
        dataset_id=str(ds.id),
        layer=ds.layer,
    )


def _is_number(v: Any) -> bool:
    try:
        float(v)
        return True
    except (TypeError, ValueError):
        return False
