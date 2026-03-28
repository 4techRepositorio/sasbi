"""Cria plano, tenant, assinatura, usuário admin e membership. Executar após migrações."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import select

from fourpro_api.core.security import hash_password
from fourpro_api.db.session import get_session_maker
from fourpro_api.models.plan import Plan
from fourpro_api.models.subscription import TenantSubscription
from fourpro_api.models.tenant import Tenant, TenantMembership
from fourpro_api.repositories.user_repository import UserRepository


def main() -> None:
    db = get_session_maker()()
    now = datetime.now(tz=UTC)
    try:
        plan = db.scalars(select(Plan).where(Plan.code == "starter")).first()
        if plan is None:
            any_plan = db.scalars(select(Plan).limit(1)).first()
            if any_plan is None:
                starter = Plan(
                    id=uuid.uuid4(),
                    name="Starter",
                    code="starter",
                    max_uploads_per_month=500,
                    max_storage_mb=5120,
                    max_concurrent_jobs=3,
                    created_at=now,
                )
                pro = Plan(
                    id=uuid.uuid4(),
                    name="Pro",
                    code="pro",
                    max_uploads_per_month=5000,
                    max_storage_mb=51200,
                    max_concurrent_jobs=10,
                    created_at=now,
                )
                db.add_all([starter, pro])
                db.commit()
                print("Planos starter e pro criados.")
                plan = starter
            else:
                plan = any_plan

        tenant = db.scalars(select(Tenant).where(Tenant.slug == "demo")).first()
        if tenant is None:
            tenant = Tenant(
                id=uuid.uuid4(),
                name="Organização Demo",
                slug="demo",
                created_at=now,
                updated_at=now,
            )
            db.add(tenant)
            db.flush()
            db.add(
                TenantSubscription(
                    id=uuid.uuid4(),
                    tenant_id=tenant.id,
                    plan_id=plan.id,
                    created_at=now,
                    updated_at=now,
                ),
            )
            db.commit()
            print(f"Tenant demo criado ({tenant.id}).")
        else:
            print(f"Tenant demo já existe ({tenant.id}).")

        urepo = UserRepository(db)
        email = "admin@local.dev"
        user = urepo.get_by_email(email)
        if user is None:
            user = urepo.create(email, hash_password("changeme"))
            print(f"Usuário {email} / changeme")
        else:
            print(f"Usuário já existe: {email}")

        m = db.scalars(
            select(TenantMembership).where(
                TenantMembership.user_id == user.id,
                TenantMembership.tenant_id == tenant.id,
            ),
        ).first()
        if m is None:
            db.add(
                TenantMembership(
                    id=uuid.uuid4(),
                    user_id=user.id,
                    tenant_id=tenant.id,
                    role="admin",
                    created_at=now,
                ),
            )
            db.commit()
            print("Membership admin vinculada ao tenant demo.")
        else:
            print("Membership já existia.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
