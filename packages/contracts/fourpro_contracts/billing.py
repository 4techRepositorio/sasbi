"""Contexto de utilizador + plano (TICKET-010) — alinhado a GET /api/v1/me/context."""

from pydantic import BaseModel, Field


class PlanSummary(BaseModel):
    """Limites do pacote associado ao tenant."""

    code: str
    name: str
    max_uploads_per_month: int = Field(ge=0)
    max_storage_mb: int = Field(ge=0)


class StorageContext(BaseModel):
    """Uso de armazenamento (bytes) vs limites: tenant (plano), utilizador e grupo opcional."""

    tenant_used_bytes: int = Field(ge=0)
    tenant_limit_mb: int = Field(ge=0)
    user_used_bytes: int = Field(ge=0)
    user_limit_mb: int | None = None
    group_used_bytes: int | None = None
    group_limit_mb: int | None = None
    group_id: str | None = None
    group_name: str | None = None


class MeContextResponse(BaseModel):
    """Resposta de contexto multitenant após autenticação."""

    user_id: str
    tenant_id: str
    tenant_name: str | None
    tenant_slug: str | None
    role: str
    plan: PlanSummary | None = None
    storage: StorageContext | None = None
