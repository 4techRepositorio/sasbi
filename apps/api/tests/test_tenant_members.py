"""Frente Core — listagem de membros do tenant (admin-only)."""

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from fourpro_api.models.audit_log import AuditLog
from fourpro_api.repositories.audit_repository import AuditAction
from tests.test_auth import _bind_tenant, _create_user


def _login_token(client: TestClient, db_session: Session, email: str, pwd: str, role: str) -> str:
    u = _create_user(db_session, email, pwd)
    _bind_tenant(db_session, u, role=role)
    r = client.post("/api/v1/auth/login", json={"email": email, "password": pwd})
    assert r.status_code == 200
    return r.json()["access_token"]


def test_tenant_members_admin_lists_self(client: TestClient, db_session: Session) -> None:
    token = _login_token(client, db_session, "adminmem@example.com", "secretpass123", "admin")
    r = client.get("/api/v1/tenant/members", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    body = r.json()
    assert "items" in body
    assert len(body["items"]) >= 1
    row = next(x for x in body["items"] if x["email"] == "adminmem@example.com")
    assert row["role"] == "admin"
    assert row["is_active"] is True
    assert "user_id" in row
    assert "membership_created_at" in row


def test_tenant_members_forbidden_for_consumer(client: TestClient, db_session: Session) -> None:
    token = _login_token(client, db_session, "cons@example.com", "secretpass123", "consumer")
    r = client.get("/api/v1/tenant/members", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 403


def test_tenant_members_list_writes_audit(client: TestClient, db_session: Session) -> None:
    token = _login_token(client, db_session, "auditmem@example.com", "secretpass123", "admin")
    r = client.get("/api/v1/tenant/members", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    items = r.json()["items"]
    rows = db_session.scalars(
        select(AuditLog).where(AuditLog.action == AuditAction.TENANT_MEMBERS_LISTED),
    ).all()
    assert len(rows) == 1
    assert rows[0].context is not None
    assert rows[0].context.get("count") == len(items)
