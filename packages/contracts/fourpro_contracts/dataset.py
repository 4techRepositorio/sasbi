from typing import Literal

from pydantic import BaseModel


class DatasetItem(BaseModel):
    """Entrada do catálogo: apenas ingestões com pipeline concluído com sucesso."""

    id: str
    tenant_id: str
    original_filename: str
    status: Literal["processed"]
    size_bytes: int
    result_summary: str | None = None
    created_at: str


class PaginatedDatasetList(BaseModel):
    items: list[DatasetItem]
    total: int
    limit: int
    offset: int
