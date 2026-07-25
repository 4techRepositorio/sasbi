"""Segurança — sessão revogada, utilizador inactivo, MFA inválido."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from fourpro_api.models.tenant import TenantMembership
from tests.test_auth import _bind_tenant, _create_user


@pytest.mark.integration
@pytest.mark.api
@pytest.mark.security
@pytest.mark.auth
def test_access_denied_after_membership_revoked(client: TestClient, db_session: Session) -> None:
    u = _create_user(db_session, "revoked@example.com", "secretpass123")
    tid = _bind_tenant(db_session, u, role="admin")
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "revoked@example.com", "password": "secretpass123"},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]

    m = db_session.scalars(
        select(TenantMembership).where(
            TenantMembership.user_id == u.id,
            TenantMembership.tenant_id == tid,
        ),
    ).first()
    assert m is not None
    db_session.delete(m)
    db_session.commit()

    r = client.get("/api/v1/me/context", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 401
    assert "revogad" in r.json()["detail"].lower() or "sessão" in r.json()["detail"].lower()


@pytest.mark.integration
@pytest.mark.api
@pytest.mark.security
@pytest.mark.auth
def test_access_denied_when_user_inactive(client: TestClient, db_session: Session) -> None:
    u = _create_user(db_session, "inactive@example.com", "secretpass123")
    _bind_tenant(db_session, u, role="admin")
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "inactive@example.com", "password": "secretpass123"},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]

    u.is_active = False
    db_session.add(u)
    db_session.commit()

    r = client.get("/api/v1/me/context", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 401


@pytest.mark.integration
@pytest.mark.api
@pytest.mark.security
@pytest.mark.auth
def test_mfa_wrong_code_rejected(client: TestClient, db_session: Session, monkeypatch) -> None:
    monkeypatch.setattr(
        "fourpro_api.services.auth_service._generate_mfa_numeric_code",
        lambda: "010203",
    )
    u = _create_user(db_session, "mfabad@example.com", "secretpass123")
    u.mfa_enabled = True
    db_session.add(u)
    db_session.commit()
    _bind_tenant(db_session, u)

    r1 = client.post(
        "/api/v1/auth/login",
        json={"email": "mfabad@example.com", "password": "secretpass123"},
    )
    assert r1.status_code == 200
    mfa_token = r1.json()["mfa_token"]

    r2 = client.post(
        "/api/v1/auth/mfa/verify",
        json={"mfa_token": mfa_token, "code": "999999"},
    )
    assert r2.status_code in (400, 401)


@pytest.mark.integration
@pytest.mark.api
@pytest.mark.security
@pytest.mark.auth
def test_bearer_missing_and_garbage_token(client: TestClient) -> None:
    assert client.get("/api/v1/me/context").status_code == 401
    r = client.get(
        "/api/v1/me/context",
        headers={"Authorization": "Bearer totally-invalid"},
    )
    assert r.status_code == 401
