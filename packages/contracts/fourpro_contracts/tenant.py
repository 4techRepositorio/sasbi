"""Contratos 4Pro_BI — membros do tenant (área administrativa, admin-only na API)."""

from pydantic import BaseModel, EmailStr, Field


class TenantMemberItem(BaseModel):
    """Um utilizador com membership no tenant atual."""

    user_id: str
    email: EmailStr
    role: str
    is_active: bool
    membership_created_at: str
    max_storage_mb: int | None = None
    quota_group_id: str | None = None
    quota_group_name: str | None = None


class TenantMemberListResponse(BaseModel):
    """Resposta de GET /tenant/members (lista completa do tenant)."""

    items: list[TenantMemberItem]


class TenantAuditLogItem(BaseModel):
    """Uma linha de `audit_log` visível só no tenant atual (admin)."""

    id: str
    created_at: str
    action: str
    actor_user_id: str | None = None
    tenant_id: str | None = None
    context: dict | None = None


class TenantAuditLogListResponse(BaseModel):
    """Resposta de GET /tenant/audit-log (paginação + filtro opcional `since` para export incremental).

    Exportação tabular: GET /tenant/audit-log/export.csv (mesmo papel `admin`, query `since` e `max_rows`).
    """

    items: list[TenantAuditLogItem]
    limit: int = Field(ge=1, le=200)
    offset: int = Field(ge=0)
    since_applied: str | None = Field(
        default=None,
        description="ISO 8601 do filtro `since` quando foi enviado na query.",
    )


class TenantQuotaGroupItem(BaseModel):
    id: str
    tenant_id: str
    name: str
    max_storage_mb: int = Field(ge=1)
    created_at: str
    updated_at: str


class TenantQuotaGroupListResponse(BaseModel):
    items: list[TenantQuotaGroupItem]


class TenantQuotaGroupCreate(BaseModel):
    name: str = Field(max_length=120)
    max_storage_mb: int = Field(ge=1)


class TenantQuotaGroupPatch(BaseModel):
    name: str | None = Field(default=None, max_length=120)
    max_storage_mb: int | None = Field(default=None, ge=1)


class MemberStorageQuotaPatch(BaseModel):
    """PATCH parcial: omitir chave = sem alteração; null remove limite ou grupo."""

    max_storage_mb: int | None = Field(default=None, ge=0)
    quota_group_id: str | None = None
