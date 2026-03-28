from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from fourpro_api.models.tenant import TenantMembership
from fourpro_api.models.user import User


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

    def get_membership(self, user_id: UUID, tenant_id: UUID) -> TenantMembership | None:
        stmt = select(TenantMembership).where(
            TenantMembership.user_id == user_id,
            TenantMembership.tenant_id == tenant_id,
        )
        return self._db.scalars(stmt).first()

    def list_members_with_users(self, tenant_id: UUID) -> list[tuple[TenantMembership, User]]:
        """Todos os membros do tenant com dados de utilizador (ordenado por email)."""
        stmt = (
            select(TenantMembership, User)
            .join(User, User.id == TenantMembership.user_id)
            .where(TenantMembership.tenant_id == tenant_id)
            .options(joinedload(TenantMembership.quota_group))
            .order_by(User.email.asc())
        )
        rows = self._db.execute(stmt).unique().all()
        return [(m, u) for m, u in rows]
