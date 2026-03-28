"""Trilho mínimo de auditoria (ações críticas de auth)."""

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from fourpro_api.models.audit_log import AuditLog
from fourpro_api.repositories.audit_repository import AuditAction
from tests.test_auth import _bind_tenant, _create_user


def test_login_creates_session_issued_audit(client: TestClient, db_session: Session) -> None:
    u = _create_user(db_session, "audit-login@example.com", "secretpass123")
    _bind_tenant(db_session, u)
    r = client.post(
        "/api/v1/auth/login",
        json={"email": "audit-login@example.com", "password": "secretpass123"},
    )
    assert r.status_code == 200
    rows = db_session.scalars(
        select(AuditLog).where(AuditLog.action == AuditAction.AUTH_SESSION_ISSUED)
    ).all()
    assert len(rows) == 1
    assert rows[0].actor_user_id == u.id
    assert rows[0].tenant_id is not None


def test_password_reset_creates_audit_events(
    client: TestClient, db_session: Session, monkeypatch
) -> None:
    monkeypatch.setattr(
        "fourpro_api.services.password_reset_service.secrets.token_urlsafe",
        lambda _n: "audit_reset_token_fixed_val",
    )
    u = _create_user(db_session, "audit-reset@example.com", "oldpw123456")
    tid = _bind_tenant(db_session, u)
    client.post("/api/v1/auth/forgot-password", json={"email": "audit-reset@example.com"})
    req_rows = db_session.scalars(
        select(AuditLog).where(AuditLog.action == AuditAction.AUTH_PASSWORD_RESET_REQUESTED),
    ).all()
    assert len(req_rows) == 1
    assert req_rows[0].actor_user_id == u.id
    assert req_rows[0].tenant_id == tid

    r = client.post(
        "/api/v1/auth/reset-password",
        json={"token": "audit_reset_token_fixed_val", "new_password": "newpw123456789"},
    )
    assert r.status_code == 200
    done = db_session.scalars(
        select(AuditLog).where(AuditLog.action == AuditAction.AUTH_PASSWORD_RESET_COMPLETED),
    ).all()
    assert len(done) == 1
    assert done[0].actor_user_id == u.id
