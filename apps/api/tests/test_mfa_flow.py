"""TICKET-003 — MFA (código por email / canal configurado)."""

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from tests.test_auth import _bind_tenant, _create_user


def test_mfa_login_and_verify(client: TestClient, db_session: Session, monkeypatch) -> None:
    monkeypatch.setattr(
        "fourpro_api.services.auth_service._generate_mfa_numeric_code",
        lambda: "010203",
    )
    u = _create_user(db_session, "mfa@example.com", "secretpass123")
    u.mfa_enabled = True
    db_session.add(u)
    db_session.commit()
    _bind_tenant(db_session, u)

    r1 = client.post(
        "/api/v1/auth/login",
        json={"email": "mfa@example.com", "password": "secretpass123"},
    )
    assert r1.status_code == 200
    body = r1.json()
    assert body.get("mfa_required") is True
    assert "mfa_token" in body

    r2 = client.post(
        "/api/v1/auth/mfa/verify",
        json={"mfa_token": body["mfa_token"], "code": "010203"},
    )
    assert r2.status_code == 200
    assert r2.json().get("access_token")
