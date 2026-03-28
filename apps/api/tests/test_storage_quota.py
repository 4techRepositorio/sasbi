"""Cotas de armazenamento: tenant (plano), utilizador e grupo."""

from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from fourpro_api.models.plan import Plan
from fourpro_api.models.subscription import TenantSubscription
from fourpro_api.models.tenant import TenantMembership, TenantQuotaGroup
from fourpro_api.repositories.ingestion_repository import IngestionRepository
from tests.test_auth import _bind_tenant, _create_user


def _csv_bytes(size: int) -> bytes:
    header = b"c\n"
    row = b"0\n"
    out = bytearray(header)
    while len(out) < size:
        out.extend(row)
    return bytes(out[:size])


def _set_plan_storage_mb(db_session: Session, tenant_id, mb: int) -> None:
    sub = db_session.scalars(
        select(TenantSubscription).where(TenantSubscription.tenant_id == tenant_id)
    ).first()
    assert sub is not None
    plan = db_session.get(Plan, sub.plan_id)
    assert plan is not None
    plan.max_storage_mb = mb
    db_session.commit()


def test_upload_rejected_when_tenant_plan_storage_exceeded(
    client: TestClient,
    db_session: Session,
) -> None:
    import os

    u = _create_user(db_session, "tstor@example.com", "secretpass123")
    tid = _bind_tenant(db_session, u, role="analyst")
    _set_plan_storage_mb(db_session, tid, 1)
    base = Path(os.environ["UPLOAD_DIR"]) / str(tid)
    base.mkdir(parents=True, exist_ok=True)
    old = base / "existing.csv"
    old.write_bytes(b"x" * 900_000)
    repo = IngestionRepository(db_session)
    repo.create(
        tenant_id=tid,
        original_filename="existing.csv",
        storage_path=str(old.resolve()),
        content_type="text/csv",
        size_bytes=900_000,
        uploaded_by_user_id=u.id,
        status="processed",
    )
    token = client.post(
        "/api/v1/auth/login",
        json={"email": "tstor@example.com", "password": "secretpass123"},
    ).json()["access_token"]
    payload = _csv_bytes(200_000)
    r = client.post(
        "/api/v1/uploads",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("more.csv", payload, "text/csv")},
    )
    assert r.status_code == 402
    assert "plano" in r.json()["detail"].lower() or "excede" in r.json()["detail"].lower()


def test_upload_rejected_when_user_storage_cap_exceeded(
    client: TestClient, db_session: Session
) -> None:
    u = _create_user(db_session, "ustor@example.com", "secretpass123")
    tid = _bind_tenant(db_session, u, role="analyst")
    m = db_session.scalars(
        select(TenantMembership).where(
            TenantMembership.user_id == u.id,
            TenantMembership.tenant_id == tid,
        ),
    ).first()
    assert m is not None
    m.max_storage_mb = 0
    db_session.commit()

    login = client.post(
        "/api/v1/auth/login",
        json={"email": "ustor@example.com", "password": "secretpass123"},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]

    payload = _csv_bytes(100)
    r = client.post(
        "/api/v1/uploads",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("a.csv", payload, "text/csv")},
    )
    assert r.status_code == 402
    assert "utilizador" in r.json()["detail"].lower()


def test_upload_rejected_when_group_storage_exceeded(
    client: TestClient, db_session: Session
) -> None:
    import uuid
    from datetime import UTC, datetime

    now = datetime.now(tz=UTC)
    admin = _create_user(db_session, "gadm@example.com", "secretpass123")
    tid = _bind_tenant(db_session, admin, role="admin")
    u1 = _create_user(db_session, "gu1@example.com", "secretpass123")
    u2 = _create_user(db_session, "gu2@example.com", "secretpass123")
    db_session.add_all(
        [
            TenantMembership(
                id=uuid.uuid4(),
                user_id=u1.id,
                tenant_id=tid,
                role="analyst",
                created_at=now,
            ),
            TenantMembership(
                id=uuid.uuid4(),
                user_id=u2.id,
                tenant_id=tid,
                role="analyst",
                created_at=now,
            ),
        ],
    )
    gid = uuid.uuid4()
    db_session.add(
        TenantQuotaGroup(
            id=gid,
            tenant_id=tid,
            name="Equipa A",
            max_storage_mb=1,
            created_at=now,
            updated_at=now,
        ),
    )
    db_session.flush()
    for u in (u1, u2):
        mm = db_session.scalars(
            select(TenantMembership).where(
                TenantMembership.user_id == u.id,
                TenantMembership.tenant_id == tid,
            ),
        ).first()
        assert mm is not None
        mm.quota_group_id = gid
    db_session.commit()

    import os

    base = Path(os.environ["UPLOAD_DIR"]) / str(tid)
    base.mkdir(parents=True, exist_ok=True)
    p1 = base / "a.csv"
    p1.write_bytes(b"z" * 600_000)
    repo = IngestionRepository(db_session)
    repo.create(
        tenant_id=tid,
        original_filename="a.csv",
        storage_path=str(p1.resolve()),
        content_type="text/csv",
        size_bytes=600_000,
        uploaded_by_user_id=u1.id,
        status="processed",
    )

    t2 = client.post(
        "/api/v1/auth/login", json={"email": "gu2@example.com", "password": "secretpass123"}
    )
    assert t2.status_code == 200
    tok2 = t2.json()["access_token"]
    payload = _csv_bytes(500_000)
    r = client.post(
        "/api/v1/uploads",
        headers={"Authorization": f"Bearer {tok2}"},
        files={"file": ("b.csv", payload, "text/csv")},
    )
    assert r.status_code == 402
    assert "grupo" in r.json()["detail"].lower()


def test_me_context_includes_storage(client: TestClient, db_session: Session) -> None:
    u = _create_user(db_session, "storctx@example.com", "secretpass123")
    _bind_tenant(db_session, u, role="analyst")
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "storctx@example.com", "password": "secretpass123"},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]
    r = client.get("/api/v1/me/context", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    st = r.json().get("storage")
    assert st is not None
    assert "tenant_used_bytes" in st
    assert "tenant_limit_mb" in st
    assert "user_used_bytes" in st
