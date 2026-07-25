"""Contratos de modelo semântico e query (TICKET-016)."""

from typing import Any, Literal

from pydantic import BaseModel, Field


class SemanticMeasure(BaseModel):
    name: str = Field(min_length=1, max_length=64)
    expression: Literal["count", "sum", "avg"] = "count"
    field: str | None = None


class SemanticDimension(BaseModel):
    name: str = Field(min_length=1, max_length=64)
    field: str


class SemanticModelCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    dataset_id: str
    dimensions: list[SemanticDimension] = Field(default_factory=list)
    measures: list[SemanticMeasure] = Field(default_factory=list)


class SemanticModelItem(BaseModel):
    id: str
    tenant_id: str
    name: str
    dataset_id: str
    dimensions: list[SemanticDimension]
    measures: list[SemanticMeasure]
    updated_at: str


class PaginatedSemanticModelList(BaseModel):
    items: list[SemanticModelItem]
    total: int
    limit: int
    offset: int


class QueryRequest(BaseModel):
    semantic_model_id: str
    measures: list[str] = Field(default_factory=list)
    dimensions: list[str] = Field(default_factory=list)
    limit: int = Field(default=100, ge=1, le=1000)


class QueryResponse(BaseModel):
    columns: list[str]
    rows: list[list[Any]]
    dataset_id: str
    layer: str | None = None
