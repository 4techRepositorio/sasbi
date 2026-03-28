"""Cria plano, tenant, assinatura, usuário admin e membership. Executar após migrações.

Credenciais de desenvolvimento (também usadas em `.github/workflows/e2e-dispatch.yml`):
- admin@local.dev / changeme (papel admin)
- consumer@local.dev / changeme (papel consumer)
"""

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

        consumer_email = "consumer@local.dev"
        cuser = urepo.get_by_email(consumer_email)
        if cuser is None:
            cuser = urepo.create(consumer_email, hash_password("changeme"))
            print(f"Usuário consumer {consumer_email} / changeme")
        else:
            print(f"Usuário consumer já existe: {consumer_email}")

        mc = db.scalars(
            select(TenantMembership).where(
                TenantMembership.user_id == cuser.id,
                TenantMembership.tenant_id == tenant.id,
            ),
        ).first()
        if mc is None:
            db.add(
                TenantMembership(
                    id=uuid.uuid4(),
                    user_id=cuser.id,
                    tenant_id=tenant.id,
                    role="consumer",
                    created_at=now,
                ),
            )
            db.commit()
            print("Membership consumer vinculada ao tenant demo.")
        elif mc.role != "consumer":
            mc.role = "consumer"
            db.commit()
            print("Membership consumer: papel atualizado para consumer.")
        else:
            print("Consumer já no tenant demo.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
