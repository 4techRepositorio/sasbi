"""Contexto /me — tenant, papel e plano (billing) alinhado a fourpro_contracts.billing."""

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from tests.test_auth import _bind_tenant, _create_user


def test_me_context_includes_plan(client: TestClient, db_session: Session) -> None:
    u = _create_user(db_session, "ctx@example.com", "secretpass123")
    _bind_tenant(db_session, u, role="analyst")
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "ctx@example.com", "password": "secretpass123"},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]
    r = client.get("/api/v1/me/context", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    body = r.json()
    assert body["role"] == "analyst"
    assert body["tenant_name"] is not None
    assert body["plan"] is not None
    assert "code" in body["plan"] and "name" in body["plan"]
    assert body["plan"]["max_uploads_per_month"] >= 0


def test_me_context_requires_auth(client: TestClient) -> None:
    r = client.get("/api/v1/me/context")
    assert r.status_code == 401
