"""TICKET-010 — enforcement de quota de upload."""

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from fourpro_api.models.plan import Plan
from fourpro_api.models.subscription import TenantSubscription

from tests.test_auth import _bind_tenant, _create_user


def test_second_upload_blocked_when_plan_limit_one(client: TestClient, db_session: Session) -> None:
    u = _create_user(db_session, "bill@example.com", "pw")
    tid = _bind_tenant(db_session, u, role="admin")
    sub = db_session.scalars(select(TenantSubscription).where(TenantSubscription.tenant_id == tid)).first()
    assert sub is not None
    plan = db_session.get(Plan, sub.plan_id)
    assert plan is not None
    plan.max_uploads_per_month = 1
    db_session.add(plan)
    db_session.commit()

    token = client.post("/api/v1/auth/login", json={"email": "bill@example.com", "password": "pw"}).json()[
        "access_token"
    ]
    files1 = {"file": ("a.csv", b"x\n1\n", "text/csv")}
    r1 = client.post(
        "/api/v1/uploads",
        headers={"Authorization": f"Bearer {token}"},
        files=files1,
    )
    assert r1.status_code == 200
    files2 = {"file": ("b.csv", b"y\n2\n", "text/csv")}
    r2 = client.post(
        "/api/v1/uploads",
        headers={"Authorization": f"Bearer {token}"},
        files=files2,
    )
    assert r2.status_code == 402
    assert "limite" in r2.json()["detail"].lower()
