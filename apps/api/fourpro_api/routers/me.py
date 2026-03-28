from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from fourpro_api.core.principal import Principal
from fourpro_api.db.session import get_db
from fourpro_api.dependencies.auth import get_current_principal
from fourpro_api.models.tenant import Tenant
from fourpro_api.repositories.plan_repository import PlanRepository

router = APIRouter(prefix="/me", tags=["me"])


@router.get("/context", summary="Contexto tenant + plano (billing TICKET-010)")
def me_context(
    principal: Annotated[Principal, Depends(get_current_principal)],
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    tenant = db.get(Tenant, principal.tenant_id)
    prepo = PlanRepository(db)
    plan = prepo.get_plan_for_tenant(principal.tenant_id)
    return {
        "user_id": str(principal.user_id),
        "tenant_id": str(principal.tenant_id),
        "tenant_name": tenant.name if tenant else None,
        "tenant_slug": tenant.slug if tenant else None,
        "role": principal.role,
        "plan": {
            "code": plan.code,
            "name": plan.name,
            "max_uploads_per_month": plan.max_uploads_per_month,
            "max_storage_mb": plan.max_storage_mb,
        }
        if plan
        else None,
    }
