"""Billing — tenant sem plano activo (402)."""

import uuid
from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from fourpro_api.core.security import hash_password
from fourpro_api.models.tenant import Tenant, TenantMembership
from fourpro_api.models.user import User


def _user_tenant_without_plan(db: Session, email: str) -> User:
    now = datetime.now(tz=UTC)
    u = User(
        email=email,
        password_hash=hash_password("secretpass123"),
        is_active=True,
        mfa_enabled=False,
        created_at=now,
        updated_at=now,
    )
    tenant = Tenant(
        id=uuid.uuid4(),
        name="NoPlan",
        slug=f"np{uuid.uuid4().hex[:8]}",
        created_at=now,
        updated_at=now,
    )
    db.add_all([u, tenant])
    db.flush()
    db.add(
        TenantMembership(
            id=uuid.uuid4(),
            user_id=u.id,
            tenant_id=tenant.id,
            role="admin",
            created_at=now,
        ),
    )
    db.commit()
    db.refresh(u)
    return u


@pytest.mark.integration
@pytest.mark.api
@pytest.mark.billing
@pytest.mark.security
def test_upload_rejected_when_tenant_has_no_plan(client: TestClient, db_session: Session) -> None:
    _user_tenant_without_plan(db_session, "noplan@example.com")
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "noplan@example.com", "password": "secretpass123"},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]
    r = client.post(
        "/api/v1/uploads",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("a.csv", b"x\n1\n", "text/csv")},
    )
    assert r.status_code == 402
    assert "plano" in r.json()["detail"].lower()
