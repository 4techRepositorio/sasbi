"""Rotas de administração do tenant (membros, quotas de armazenamento) — Backend Core."""

import csv
import io
import json
from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import Response
from fourpro_contracts.tenant import (
    MemberStorageQuotaPatch,
    TenantAuditLogItem,
    TenantAuditLogListResponse,
    TenantMemberItem,
    TenantMemberListResponse,
    TenantQuotaGroupCreate,
    TenantQuotaGroupItem,
    TenantQuotaGroupListResponse,
    TenantQuotaGroupPatch,
)
from sqlalchemy.orm import Session

from fourpro_api.core.principal import Principal
from fourpro_api.db.session import get_db
from fourpro_api.dependencies.auth import require_roles
from fourpro_api.limiter import limiter
from fourpro_api.repositories.audit_repository import AuditAction, AuditRepository
from fourpro_api.repositories.membership_repository import MembershipRepository
from fourpro_api.repositories.quota_group_repository import QuotaGroupRepository

router = APIRouter(prefix="/tenant", tags=["tenant"])


def _group_item(g) -> TenantQuotaGroupItem:
    return TenantQuotaGroupItem(
        id=str(g.id),
        tenant_id=str(g.tenant_id),
        name=g.name,
        max_storage_mb=g.max_storage_mb,
        created_at=g.created_at.isoformat(),
        updated_at=g.updated_at.isoformat(),
    )


@router.get(
    "/members", response_model=TenantMemberListResponse, summary="Listar membros do tenant (admin)"
)
@limiter.limit("60/minute")
def list_tenant_members(
    request: Request,
    principal: Annotated[Principal, Depends(require_roles("admin"))],
    db: Annotated[Session, Depends(get_db)],
) -> TenantMemberListResponse:
    repo = MembershipRepository(db)
    rows = repo.list_members_with_users(principal.tenant_id)
    items = [
        TenantMemberItem(
            user_id=str(u.id),
            email=u.email,
            role=m.role,
            is_active=u.is_active,
            membership_created_at=m.created_at.isoformat(),
            max_storage_mb=m.max_storage_mb,
            quota_group_id=str(m.quota_group_id) if m.quota_group_id else None,
            quota_group_name=m.quota_group.name if m.quota_group else None,
        )
        for m, u in rows
    ]
    AuditRepository(db).record(
        action=AuditAction.TENANT_MEMBERS_LISTED,
        actor_user_id=principal.user_id,
        tenant_id=principal.tenant_id,
        context={"count": len(items)},
    )
    return TenantMemberListResponse(items=items)


@router.get(
    "/audit-log",
    response_model=TenantAuditLogListResponse,
    summary="Listar auditoria do tenant (admin; consulta / export incremental)",
)
@limiter.limit("60/minute")
def list_tenant_audit_log(
    request: Request,
    principal: Annotated[Principal, Depends(require_roles("admin"))],
    db: Annotated[Session, Depends(get_db)],
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    since: datetime | None = Query(
        default=None,
        description=(
            "Incluir apenas eventos com created_at >= since (UTC, ISO 8601). "
            "Útil para SIEM a poll incremental."
        ),
    ),
) -> TenantAuditLogListResponse:
    repo = AuditRepository(db)
    rows = repo.list_for_tenant(
        principal.tenant_id,
        limit=limit,
        offset=offset,
        since=since,
    )
    items = [
        TenantAuditLogItem(
            id=str(r.id),
            created_at=r.created_at.isoformat(),
            action=r.action,
            actor_user_id=str(r.actor_user_id) if r.actor_user_id else None,
            tenant_id=str(r.tenant_id) if r.tenant_id else None,
            context=r.context,
        )
        for r in rows
    ]
    return TenantAuditLogListResponse(
        items=items,
        limit=limit,
        offset=offset,
        since_applied=since.isoformat() if since else None,
    )


@router.get(
    "/audit-log/export.csv",
    summary="Exportar auditoria do tenant em CSV (admin; até max_rows linhas)",
    response_class=Response,
)
@limiter.limit("12/minute")
def export_tenant_audit_log_csv(
    request: Request,
    principal: Annotated[Principal, Depends(require_roles("admin"))],
    db: Annotated[Session, Depends(get_db)],
    since: datetime | None = Query(
        default=None,
        description="Incluir apenas eventos com created_at >= since (UTC, ISO 8601).",
    ),
    max_rows: int = Query(
        default=5000,
        ge=1,
        le=10_000,
        description="Teto de linhas de dados (cabeçalho não conta).",
    ),
) -> Response:
    repo = AuditRepository(db)
    rows = repo.list_for_tenant_export(principal.tenant_id, since=since, max_rows=max_rows)
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(("id", "created_at", "action", "actor_user_id", "tenant_id", "context_json"))
    for r in rows:
        writer.writerow(
            (
                str(r.id),
                r.created_at.isoformat(),
                r.action,
                str(r.actor_user_id) if r.actor_user_id else "",
                str(r.tenant_id) if r.tenant_id else "",
                json.dumps(r.context, ensure_ascii=False) if r.context else "",
            )
        )
    body = ("\ufeff" + buf.getvalue()).encode("utf-8")
    return Response(
        content=body,
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": 'attachment; filename="tenant-audit-export.csv"',
        },
    )


@router.get(
    "/quota-groups",
    response_model=TenantQuotaGroupListResponse,
    summary="Listar grupos de quota de armazenamento (admin)",
)
@limiter.limit("60/minute")
def list_quota_groups(
    request: Request,
    principal: Annotated[Principal, Depends(require_roles("admin"))],
    db: Annotated[Session, Depends(get_db)],
) -> TenantQuotaGroupListResponse:
    repo = QuotaGroupRepository(db)
    rows = repo.list_for_tenant(principal.tenant_id)
    return TenantQuotaGroupListResponse(items=[_group_item(g) for g in rows])


@router.post(
    "/quota-groups",
    response_model=TenantQuotaGroupItem,
    status_code=status.HTTP_201_CREATED,
    summary="Criar grupo de quota (admin)",
)
@limiter.limit("30/minute")
def create_quota_group(
    request: Request,
    principal: Annotated[Principal, Depends(require_roles("admin"))],
    db: Annotated[Session, Depends(get_db)],
    body: TenantQuotaGroupCreate,
) -> TenantQuotaGroupItem:
    repo = QuotaGroupRepository(db)
    g = repo.create(
        tenant_id=principal.tenant_id, name=body.name.strip(), max_storage_mb=body.max_storage_mb
    )
    AuditRepository(db).record(
        action=AuditAction.TENANT_QUOTA_GROUP_CREATED,
        actor_user_id=principal.user_id,
        tenant_id=principal.tenant_id,
        context={"group_id": str(g.id), "name": g.name, "max_storage_mb": g.max_storage_mb},
    )
    return _group_item(g)


@router.patch(
    "/quota-groups/{group_id}",
    response_model=TenantQuotaGroupItem,
    summary="Atualizar grupo de quota (admin)",
)
@limiter.limit("30/minute")
def patch_quota_group(
    request: Request,
    principal: Annotated[Principal, Depends(require_roles("admin"))],
    db: Annotated[Session, Depends(get_db)],
    group_id: UUID,
    body: TenantQuotaGroupPatch,
) -> TenantQuotaGroupItem:
    repo = QuotaGroupRepository(db)
    g = repo.get(group_id, principal.tenant_id)
    if g is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Grupo não encontrado")
    patch = body.model_dump(exclude_unset=True)
    if not patch:
        return _group_item(g)
    repo.update(g, name=patch.get("name"), max_storage_mb=patch.get("max_storage_mb"))
    db.refresh(g)
    AuditRepository(db).record(
        action=AuditAction.TENANT_QUOTA_GROUP_UPDATED,
        actor_user_id=principal.user_id,
        tenant_id=principal.tenant_id,
        context={"group_id": str(g.id), "patch": patch},
    )
    return _group_item(g)


@router.delete(
    "/quota-groups/{group_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None,
    summary="Eliminar grupo de quota (admin); memberships ficam sem grupo",
)
@limiter.limit("30/minute")
def delete_quota_group(
    request: Request,
    principal: Annotated[Principal, Depends(require_roles("admin"))],
    db: Annotated[Session, Depends(get_db)],
    group_id: UUID,
) -> None:
    repo = QuotaGroupRepository(db)
    g = repo.get(group_id, principal.tenant_id)
    if g is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Grupo não encontrado")
    AuditRepository(db).record(
        action=AuditAction.TENANT_QUOTA_GROUP_DELETED,
        actor_user_id=principal.user_id,
        tenant_id=principal.tenant_id,
        context={"group_id": str(g.id)},
    )
    repo.delete(g)


@router.patch(
    "/members/{user_id}/quotas",
    summary="Definir cota por utilizador e/ou grupo (admin); omitir campo = sem alteração",
)
@limiter.limit("30/minute")
def patch_member_storage_quotas(
    request: Request,
    principal: Annotated[Principal, Depends(require_roles("admin"))],
    db: Annotated[Session, Depends(get_db)],
    user_id: UUID,
    body: MemberStorageQuotaPatch,
) -> dict[str, str]:
    mrepo = MembershipRepository(db)
    m = mrepo.get_membership(user_id, principal.tenant_id)
    if m is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Membro não encontrado")
    patch = body.model_dump(exclude_unset=True)
    if "max_storage_mb" in patch:
        m.max_storage_mb = patch["max_storage_mb"]
    if "quota_group_id" in patch:
        raw = patch["quota_group_id"]
        if raw is None:
            m.quota_group_id = None
        else:
            try:
                gid = UUID(raw)
            except ValueError as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="quota_group_id inválido",
                ) from e
            g = QuotaGroupRepository(db).get(gid, principal.tenant_id)
            if g is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Grupo inexistente neste tenant",
                )
            m.quota_group_id = gid
    db.add(m)
    db.commit()
    AuditRepository(db).record(
        action=AuditAction.TENANT_MEMBER_QUOTAS_UPDATED,
        actor_user_id=principal.user_id,
        tenant_id=principal.tenant_id,
        context={"target_user_id": str(user_id), "patch_keys": list(patch.keys())},
    )
    return {"detail": "Quotas atualizadas"}
