"""Contratos de modelo semântico e query agregada (TICKET-016)."""

from typing import Any, Literal

from pydantic import BaseModel, Field

AggregationOp = Literal["count", "sum", "avg", "min", "max"]
FieldRole = Literal["dimension", "measure", "attribute"]


class SemanticField(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    source_column: str = Field(min_length=1, max_length=120)
    role: FieldRole = "attribute"
    data_type: str = "string"
    label: str | None = None


class SemanticModelCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    dataset_id: str
    description: str | None = None
    fields: list[SemanticField] = Field(default_factory=list)


class SemanticModelPatch(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    fields: list[SemanticField] | None = None


class SemanticModelItem(BaseModel):
    id: str
    tenant_id: str
    name: str
    dataset_id: str
    description: str | None = None
    fields: list[SemanticField]
    created_at: str
    updated_at: str


class PaginatedSemanticModelList(BaseModel):
    items: list[SemanticModelItem]
    total: int
    limit: int
    offset: int


class QueryMeasure(BaseModel):
    field: str
    op: AggregationOp
    alias: str | None = None


class QueryRequest(BaseModel):
    semantic_model_id: str
    measures: list[QueryMeasure] = Field(min_length=1, max_length=20)
    dimensions: list[str] = Field(default_factory=list, max_length=10)
    filters: dict[str, Any] = Field(default_factory=dict)
    limit: int = Field(default=500, ge=1, le=5000)


class QueryResponse(BaseModel):
    columns: list[str]
    rows: list[dict[str, Any]]
    row_count: int
    truncated: bool = False
    semantic_model_id: str
    dataset_id: str
