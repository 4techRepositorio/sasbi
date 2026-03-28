from typing import Literal, TypeAlias

from pydantic import BaseModel

# Ciclo de vida do registo `file_ingestions` (upload → worker). Valores persistidos na API/worker.
IngestionLifecycleStatus: TypeAlias = Literal[
    "uploaded",
    "validating",
    "parsing",
    "processed",
    "failed",
]


class IngestionItem(BaseModel):
    id: str
    tenant_id: str
    original_filename: str
    status: IngestionLifecycleStatus
    size_bytes: int
    content_type: str | None = None
    content_sha256: str | None = None
    uploaded_by_user_id: str | None = None
    friendly_error: str | None = None
    result_summary: str | None = None
    created_at: str


class UploadCreatedResponse(BaseModel):
    """Resposta do POST /uploads após armazenamento (estado inicial `uploaded`)."""

    id: str
    tenant_id: str
    status: Literal["uploaded"]
    original_filename: str
    size_bytes: int
    content_type: str | None = None
    content_sha256: str
    uploaded_by_user_id: str
    created_at: str
