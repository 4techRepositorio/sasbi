"""Billing — arestas (bytes inválidos, storage context com grupo)."""

import uuid
from datetime import UTC, datetime

import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from fourpro_api.core.principal import Principal
from fourpro_api.core.security import hash_password
from fourpro_api.models.plan import Plan
from fourpro_api.models.subscription import TenantSubscription
from fourpro_api.models.tenant import Tenant, TenantMembership, TenantQuotaGroup
from fourpro_api.models.user import User
from fourpro_api.services.billing_service import BillingService


def _seed_with_group(db: Session) -> tuple[Principal, TenantQuotaGroup]:
    now = datetime.now(tz=UTC)
    plan = Plan(
        id=uuid.uuid4(),
        name="P",
        code=f"p{uuid.uuid4().hex[:8]}",
        max_uploads_per_month=10,
        max_storage_mb=100,
        max_concurrent_jobs=1,
        created_at=now,
    )
    tenant = Tenant(
        id=uuid.uuid4(),
        name="T",
        slug=f"t{uuid.uuid4().hex[:8]}",
        created_at=now,
        updated_at=now,
    )
    user = User(
        email=f"b{uuid.uuid4().hex[:8]}@example.com",
        password_hash=hash_password("x"),
        is_active=True,
        mfa_enabled=False,
        created_at=now,
        updated_at=now,
    )
    group = TenantQuotaGroup(
        id=uuid.uuid4(),
        tenant_id=tenant.id,
        name="G",
        max_storage_mb=50,
        created_at=now,
        updated_at=now,
    )
    db.add_all([plan, tenant, user, group])
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
    db.add(
        TenantMembership(
            id=uuid.uuid4(),
            user_id=user.id,
            tenant_id=tenant.id,
            role="admin",
            quota_group_id=group.id,
            created_at=now,
        ),
    )
    db.commit()
    return Principal(user_id=user.id, tenant_id=tenant.id, role="admin"), group


@pytest.mark.unit
@pytest.mark.billing
def test_ensure_storage_rejects_negative_bytes(db_session: Session) -> None:
    principal, _ = _seed_with_group(db_session)
    svc = BillingService(db_session)
    with pytest.raises(HTTPException) as exc:
        svc.ensure_storage_for_new_upload(principal.tenant_id, principal.user_id, -1)
    assert exc.value.status_code == 400


@pytest.mark.unit
@pytest.mark.billing
def test_storage_context_includes_quota_group(db_session: Session) -> None:
    principal, group = _seed_with_group(db_session)
    svc = BillingService(db_session)
    ctx = svc.build_me_context(principal)
    assert ctx.storage is not None
    assert ctx.storage.group_id == str(group.id)
    assert ctx.storage.group_name == "G"
    assert ctx.plan is not None
