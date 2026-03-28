from uuid import UUID

from fastapi import HTTPException, status
from fourpro_contracts.billing import MeContextResponse, PlanSummary, StorageContext
from sqlalchemy.orm import Session

from fourpro_api.core.principal import Principal
from fourpro_api.models.tenant import Tenant, TenantQuotaGroup
from fourpro_api.repositories.ingestion_repository import IngestionRepository
from fourpro_api.repositories.membership_repository import MembershipRepository
from fourpro_api.repositories.plan_repository import PlanRepository


def _mb_to_bytes(mb: int) -> int:
    return mb * 1024 * 1024


class BillingService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._plans = PlanRepository(db)
        self._ingestions = IngestionRepository(db)
        self._members = MembershipRepository(db)

    def plan_summary_for_tenant(self, tenant_id: UUID) -> PlanSummary | None:
        """Resumo do plano ativo (contrato billing).

        Reutilizável por upload/worker sem duplicar mapeamento.
        """
        plan = self._plans.get_plan_for_tenant(tenant_id)
        if plan is None:
            return None
        return PlanSummary(
            code=plan.code,
            name=plan.name,
            max_uploads_per_month=plan.max_uploads_per_month,
            max_storage_mb=plan.max_storage_mb,
        )

    def _storage_context(self, principal: Principal) -> StorageContext:
        tid = principal.tenant_id
        uid = principal.user_id
        tenant_used = self._ingestions.sum_size_bytes_for_tenant(tid)
        user_used = self._ingestions.sum_size_bytes_for_user_in_tenant(uid, tid)
        plan = self._plans.get_plan_for_tenant(tid)
        tenant_limit_mb = plan.max_storage_mb if plan else 0
        m = self._members.get_membership(uid, tid)
        user_limit_mb = m.max_storage_mb if m else None
        group_used: int | None = None
        group_limit_mb: int | None = None
        group_id: str | None = None
        group_name: str | None = None
        if m and m.quota_group_id:
            g = self._db.get(TenantQuotaGroup, m.quota_group_id)
            if g is not None and g.tenant_id == tid:
                group_used = self._ingestions.sum_size_bytes_for_quota_group(g.id, tid)
                group_limit_mb = g.max_storage_mb
                group_id = str(g.id)
                group_name = g.name
        return StorageContext(
            tenant_used_bytes=tenant_used,
            tenant_limit_mb=tenant_limit_mb,
            user_used_bytes=user_used,
            user_limit_mb=user_limit_mb,
            group_used_bytes=group_used,
            group_limit_mb=group_limit_mb,
            group_id=group_id,
            group_name=group_name,
        )

    def build_me_context(self, principal: Principal) -> MeContextResponse:
        tenant = self._db.get(Tenant, principal.tenant_id)
        return MeContextResponse(
            user_id=str(principal.user_id),
            tenant_id=str(principal.tenant_id),
            tenant_name=tenant.name if tenant else None,
            tenant_slug=tenant.slug if tenant else None,
            role=principal.role,
            plan=self.plan_summary_for_tenant(principal.tenant_id),
            storage=self._storage_context(principal),
        )

    def ensure_upload_allowed(self, tenant_id: UUID) -> None:
        plan = self._plans.get_plan_for_tenant(tenant_id)
        if plan is None:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="Tenant sem plano ativo",
            )
        used = self._ingestions.count_uploads_this_month(tenant_id)
        if used >= plan.max_uploads_per_month:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="Limite mensal de uploads do plano excedido",
            )

    def ensure_storage_for_new_upload(
        self, tenant_id: UUID, user_id: UUID, additional_bytes: int
    ) -> None:
        """Cotas: plano (tenant) + opcional por utilizador + opcional por grupo de quota."""
        if additional_bytes < 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tamanho inválido")
        plan = self._plans.get_plan_for_tenant(tenant_id)
        if plan is None:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="Tenant sem plano ativo",
            )
        tenant_cap = _mb_to_bytes(plan.max_storage_mb)
        tenant_used = self._ingestions.sum_size_bytes_for_tenant(tenant_id)
        if tenant_used + additional_bytes > tenant_cap:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="Armazenamento do tenant excede o limite do plano",
            )

        m = self._members.get_membership(user_id, tenant_id)
        if m is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Sem membership no tenant",
            )
        if m.max_storage_mb is not None:
            user_cap = _mb_to_bytes(m.max_storage_mb)
            user_used = self._ingestions.sum_size_bytes_for_user_in_tenant(user_id, tenant_id)
            if user_used + additional_bytes > user_cap:
                raise HTTPException(
                    status_code=status.HTTP_402_PAYMENT_REQUIRED,
                    detail="Limite de armazenamento do utilizador excedido",
                )
        if m.quota_group_id is not None:
            g = self._db.get(TenantQuotaGroup, m.quota_group_id)
            if g is None or g.tenant_id != tenant_id:
                return
            group_cap = _mb_to_bytes(g.max_storage_mb)
            group_used = self._ingestions.sum_size_bytes_for_quota_group(
                m.quota_group_id, tenant_id
            )
            if group_used + additional_bytes > group_cap:
                raise HTTPException(
                    status_code=status.HTTP_402_PAYMENT_REQUIRED,
                    detail="Limite de armazenamento do grupo excedido",
                )
