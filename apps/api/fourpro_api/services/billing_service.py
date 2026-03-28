from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from fourpro_api.repositories.ingestion_repository import IngestionRepository
from fourpro_api.repositories.plan_repository import PlanRepository


class BillingService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._plans = PlanRepository(db)
        self._ingestions = IngestionRepository(db)

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
