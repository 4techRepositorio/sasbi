from pydantic import BaseModel


class DatasetItem(BaseModel):
    id: str
    tenant_id: str
    original_filename: str
    status: str
    size_bytes: int
    result_summary: str | None = None
    created_at: str


class PaginatedDatasetList(BaseModel):
    items: list[DatasetItem]
    total: int
    limit: int
    offset: int
