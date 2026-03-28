from pydantic import BaseModel


class IngestionItem(BaseModel):
    id: str
    tenant_id: str
    original_filename: str
    status: str
    size_bytes: int
    friendly_error: str | None = None
    result_summary: str | None = None
    created_at: str
