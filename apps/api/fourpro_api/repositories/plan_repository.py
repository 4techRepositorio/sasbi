from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from fourpro_api.models.plan import Plan
from fourpro_api.models.subscription import TenantSubscription


class PlanRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def get_plan_for_tenant(self, tenant_id: UUID) -> Plan | None:
        stmt = select(TenantSubscription).where(TenantSubscription.tenant_id == tenant_id)
        sub = self._db.scalars(stmt).first()
        if sub is None:
            return None
        return self._db.get(Plan, sub.plan_id)
