from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from fourpro_api.models.tenant import TenantMembership


class MembershipRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def get_default_membership(self, user_id: UUID) -> TenantMembership | None:
        stmt = (
            select(TenantMembership)
            .where(TenantMembership.user_id == user_id)
            .order_by(TenantMembership.created_at.asc())
            .limit(1)
        )
        return self._db.scalars(stmt).first()

    def get_role(self, user_id: UUID, tenant_id: UUID) -> str | None:
        stmt = select(TenantMembership).where(
            TenantMembership.user_id == user_id,
            TenantMembership.tenant_id == tenant_id,
        )
        m = self._db.scalars(stmt).first()
        return m.role if m else None
