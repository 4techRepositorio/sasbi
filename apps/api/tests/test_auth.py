import uuid
from datetime import UTC, datetime

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from fourpro_api.core.security import hash_password
from fourpro_api.models.plan import Plan
from fourpro_api.models.subscription import TenantSubscription
from fourpro_api.models.tenant import Tenant, TenantMembership
from fourpro_api.models.user import User


def _create_user(db: Session, email: str, password: str) -> User:
    now = datetime.now(tz=UTC)
    u = User(
        email=email,
        password_hash=hash_password(password),
        is_active=True,
        mfa_enabled=False,
        created_at=now,
        updated_at=now,
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


def _bind_tenant(db: Session, user: User, role: str = "admin") -> uuid.UUID:
    now = datetime.now(tz=UTC)
    plan = Plan(
        id=uuid.uuid4(),
        name="Test",
        code=f"t{uuid.uuid4().hex[:8]}",
        max_uploads_per_month=100,
        max_storage_mb=1000,
        max_concurrent_jobs=2,
        created_at=now,
    )
    tenant = Tenant(
        id=uuid.uuid4(),
        name="T",
        slug=f"t{uuid.uuid4().hex[:8]}",
        created_at=now,
        updated_at=now,
    )
    db.add_all([plan, tenant])
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
            role=role,
            created_at=now,
        ),
    )
    db.commit()
    return tenant.id


def test_login_success(client: TestClient, db_session: Session) -> None:
    u = _create_user(db_session, "a@example.com", "secretpass123")
    _bind_tenant(db_session, u)
    r = client.post(
        "/api/v1/auth/login",
        json={"email": "a@example.com", "password": "secretpass123"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["token_type"] == "bearer"
    assert "access_token" in body and "refresh_token" in body
    assert body["expires_in"] > 0
    assert body.get("mfa_required") is False
    assert body["tenant_id"] is not None


def test_login_invalid_password_same_message(client: TestClient, db_session: Session) -> None:
    u = _create_user(db_session, "b@example.com", "rightpassword")
    _bind_tenant(db_session, u)
    r = client.post(
        "/api/v1/auth/login",
        json={"email": "b@example.com", "password": "wrong"},
    )
    assert r.status_code == 401
    assert r.json()["detail"] == "Credenciais inválidas"


def test_login_unknown_email(client: TestClient) -> None:
    r = client.post(
        "/api/v1/auth/login",
        json={"email": "nobody@example.com", "password": "x"},
    )
    assert r.status_code == 401
    assert r.json()["detail"] == "Credenciais inválidas"


def test_login_no_tenant_forbidden(client: TestClient, db_session: Session) -> None:
    _create_user(db_session, "orphan@example.com", "pw")
    r = client.post(
        "/api/v1/auth/login",
        json={"email": "orphan@example.com", "password": "pw"},
    )
    assert r.status_code == 403


def test_refresh_rotates(client: TestClient, db_session: Session) -> None:
    u = _create_user(db_session, "c@example.com", "pw")
    _bind_tenant(db_session, u)
    r1 = client.post(
        "/api/v1/auth/login",
        json={"email": "c@example.com", "password": "pw"},
    )
    old_refresh = r1.json()["refresh_token"]
    r2 = client.post("/api/v1/auth/refresh", json={"refresh_token": old_refresh})
    assert r2.status_code == 200
    assert r2.json()["refresh_token"] != old_refresh
    r3 = client.post("/api/v1/auth/refresh", json={"refresh_token": old_refresh})
    assert r3.status_code == 401
