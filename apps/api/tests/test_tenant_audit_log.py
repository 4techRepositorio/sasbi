"""GET /tenant/audit-log — admin-only, isolamento por tenant, filtro since; export CSV."""

import csv
import io
from datetime import UTC, datetime, timedelta
from uuid import UUID

from fastapi.testclient import TestClient
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from fourpro_api.models.audit_log import AuditLog
from fourpro_api.repositories.audit_repository import AuditRepository
from tests.test_auth import _bind_tenant, _create_user


def _admin_token(client: TestClient, db_session: Session, email: str) -> str:
    u = _create_user(db_session, email, "secretpass123")
    _bind_tenant(db_session, u, role="admin")
    r = client.post("/api/v1/auth/login", json={"email": email, "password": "secretpass123"})
    assert r.status_code == 200
    return r.json()["access_token"]


def test_tenant_audit_log_admin_does_not_see_other_tenant(
    client: TestClient,
    db_session: Session,
) -> None:
    token_a = _admin_token(client, db_session, "audita@example.com")
    ta = client.post(
        "/api/v1/auth/login", json={"email": "audita@example.com", "password": "secretpass123"}
    )
    tid_a = ta.json()["tenant_id"]

    u_b = _create_user(db_session, "other-tenant-user@example.com", "secretpass123")
    tid_b = _bind_tenant(db_session, u_b, role="admin")
    assert str(tid_b) != tid_a
    AuditRepository(db_session).record(
        action="isolation.marker",
        tenant_id=tid_b,
        context={"marker": True},
    )

    r = client.get(
        "/api/v1/tenant/audit-log",
        headers={"Authorization": f"Bearer {token_a}"},
    )
    assert r.status_code == 200
    body = r.json()
    assert "items" in body
    assert body["limit"] == 50
    assert body["offset"] == 0
    actions = [x["action"] for x in body["items"]]
    assert "isolation.marker" not in actions
    for item in body["items"]:
        if item.get("tenant_id") is not None:
            assert item["tenant_id"] == tid_a


def test_tenant_audit_log_forbidden_for_non_admin(client: TestClient, db_session: Session) -> None:
    u = _create_user(db_session, "auditc@example.com", "secretpass123")
    _bind_tenant(db_session, u, role="analyst")
    tr = client.post(
        "/api/v1/auth/login", json={"email": "auditc@example.com", "password": "secretpass123"}
    )
    token = tr.json()["access_token"]
    r = client.get("/api/v1/tenant/audit-log", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 403


def test_tenant_audit_log_since_filter(client: TestClient, db_session: Session) -> None:
    token = _admin_token(client, db_session, "auditd@example.com")
    login = client.post(
        "/api/v1/auth/login", json={"email": "auditd@example.com", "password": "secretpass123"}
    )
    tid = login.json()["tenant_id"]

    tenant_uuid = UUID(tid)
    now = datetime.now(tz=UTC)
    repo = AuditRepository(db_session)
    repo.record(
        action="test.old",
        tenant_id=tenant_uuid,
        context={"n": 1},
    )
    old = db_session.scalars(select(AuditLog).where(AuditLog.action == "test.old")).one()
    db_session.execute(
        update(AuditLog).where(AuditLog.id == old.id).values(created_at=now - timedelta(days=2)),
    )
    db_session.commit()

    repo.record(
        action="test.new",
        tenant_id=tenant_uuid,
        context={"n": 2},
    )

    since = (now - timedelta(days=1)).replace(microsecond=0).isoformat()
    r = client.get(
        "/api/v1/tenant/audit-log",
        params={"since": since},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    actions = {x["action"] for x in r.json()["items"]}
    assert "test.new" in actions
    assert "test.old" not in actions
    assert r.json()["since_applied"] is not None


def test_tenant_audit_log_export_csv_admin(
    client: TestClient,
    db_session: Session,
) -> None:
    token = _admin_token(client, db_session, "auditcsv@example.com")
    r = client.get(
        "/api/v1/tenant/audit-log/export.csv",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    assert r.headers.get("content-type", "").startswith("text/csv")
    assert "attachment" in (r.headers.get("content-disposition") or "").lower()
    text = r.content.decode("utf-8-sig")
    rows = list(csv.reader(io.StringIO(text)))
    assert len(rows) >= 2
    assert rows[0] == [
        "id",
        "created_at",
        "action",
        "actor_user_id",
        "tenant_id",
        "context_json",
    ]


def test_tenant_audit_log_export_csv_forbidden_for_non_admin(
    client: TestClient,
    db_session: Session,
) -> None:
    u = _create_user(db_session, "auditcsv2@example.com", "secretpass123")
    _bind_tenant(db_session, u, role="analyst")
    tr = client.post(
        "/api/v1/auth/login",
        json={"email": "auditcsv2@example.com", "password": "secretpass123"},
    )
    token = tr.json()["access_token"]
    r = client.get(
        "/api/v1/tenant/audit-log/export.csv",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 403


def test_tenant_audit_log_export_csv_tenant_isolation(
    client: TestClient,
    db_session: Session,
) -> None:
    token_a = _admin_token(client, db_session, "auditcsv3@example.com")
    u_b = _create_user(db_session, "auditcsv3-b@example.com", "secretpass123")
    tid_b = _bind_tenant(db_session, u_b, role="admin")
    AuditRepository(db_session).record(
        action="csv.isolation.marker",
        tenant_id=tid_b,
        context={"x": 1},
    )
    r = client.get(
        "/api/v1/tenant/audit-log/export.csv",
        headers={"Authorization": f"Bearer {token_a}"},
    )
    assert r.status_code == 200
    text = r.content.decode("utf-8-sig")
    assert "csv.isolation.marker" not in text
