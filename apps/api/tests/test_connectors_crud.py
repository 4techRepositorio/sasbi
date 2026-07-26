"""API — CRUD fontes, test connection e sync-runs (cobertura BI)."""

import os
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from fourpro_api.config import reset_settings_cache
from fourpro_api.jobs.connector_sync import run_data_source_sync
from fourpro_api.repositories.data_source_repository import DataSourceRepository
from tests.test_auth import _bind_tenant, _create_user


@pytest.fixture(autouse=True)
def _sync_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("INGESTION_SYNC_PARSE_FALLBACK", "1")
    monkeypatch.delenv("REDIS_URL", raising=False)
    os.environ.pop("REDIS_URL", None)
    reset_settings_cache()
    yield
    reset_settings_cache()


def _token(client: TestClient, db: Session, email: str) -> str:
    u = _create_user(db, email, "pw")
    _bind_tenant(db, u, role="admin")
    return client.post("/api/v1/auth/login", json={"email": email, "password": "pw"}).json()[
        "access_token"
    ]


@pytest.mark.integration
@pytest.mark.api
def test_data_source_crud_test_and_sync_runs(client: TestClient, db_session: Session) -> None:
    token = _token(client, db_session, "crudsrc@example.com")
    h = {"Authorization": f"Bearer {token}"}

    bad = client.post(
        "/api/v1/data-sources",
        headers=h,
        json={"name": "X", "connector_type": "oracle", "config": {}},
    )
    # Contrato Pydantic (enum) rejeita antes do router.
    assert bad.status_code == 422

    created = client.post(
        "/api/v1/data-sources",
        headers=h,
        json={"name": "File A", "connector_type": "file", "config": {}},
    )
    assert created.status_code == 201
    sid = created.json()["id"]

    got = client.get(f"/api/v1/data-sources/{sid}", headers=h)
    assert got.status_code == 200
    assert got.json()["name"] == "File A"

    patched = client.patch(
        f"/api/v1/data-sources/{sid}",
        headers=h,
        json={"name": "File B", "secret": "new-secret", "status": "active"},
    )
    assert patched.status_code == 200
    assert patched.json()["name"] == "File B"
    assert patched.json()["has_secret"] is True

    tested = client.post(f"/api/v1/data-sources/{sid}/test", headers=h)
    assert tested.status_code == 200
    assert tested.json()["ok"] is True

    sync = client.post(f"/api/v1/data-sources/{sid}/sync", headers=h)
    assert sync.status_code == 200

    runs = client.get(f"/api/v1/data-sources/{sid}/sync-runs", headers=h)
    assert runs.status_code == 200
    assert len(runs.json()) >= 1

    deleted = client.delete(f"/api/v1/data-sources/{sid}", headers=h)
    assert deleted.status_code == 204
    assert client.get(f"/api/v1/data-sources/{sid}", headers=h).status_code == 404


@pytest.mark.integration
@pytest.mark.api
@pytest.mark.tenant_isolation
def test_data_source_mutations_404_cross_tenant(client: TestClient, db_session: Session) -> None:
    t1 = _token(client, db_session, "srca@example.com")
    t2 = _token(client, db_session, "srcb@example.com")
    src = client.post(
        "/api/v1/data-sources",
        headers={"Authorization": f"Bearer {t1}"},
        json={"name": "Mine", "connector_type": "file", "config": {}},
    ).json()
    sid = src["id"]
    h2 = {"Authorization": f"Bearer {t2}"}
    patch = client.patch(f"/api/v1/data-sources/{sid}", headers=h2, json={"name": "H"})
    assert patch.status_code == 404
    assert client.delete(f"/api/v1/data-sources/{sid}", headers=h2).status_code == 404
    assert client.post(f"/api/v1/data-sources/{sid}/test", headers=h2).status_code == 404
    assert client.post(f"/api/v1/data-sources/{sid}/sync", headers=h2).status_code == 404
    assert client.get(f"/api/v1/data-sources/{sid}/sync-runs", headers=h2).status_code == 404


@pytest.mark.integration
@pytest.mark.api
def test_rest_json_source_sync_demo_fallback(client: TestClient, db_session: Session) -> None:
    token = _token(client, db_session, "restsrc@example.com")
    h = {"Authorization": f"Bearer {token}"}
    created = client.post(
        "/api/v1/data-sources",
        headers=h,
        json={
            "name": "REST",
            "connector_type": "rest_json",
            "config": {"url": "https://example.com/api.json", "allowlist_hosts": ["example.com"]},
        },
    )
    assert created.status_code == 201
    sync = client.post(f"/api/v1/data-sources/{created.json()['id']}/sync", headers=h)
    assert sync.status_code == 200
    assert sync.json()["status"] in ("processed", "queued", "failed", "running")


@pytest.mark.unit
@pytest.mark.ingestion
def test_connector_sync_missing_run_and_unknown_type(db_session: Session) -> None:
    run_data_source_sync(str(uuid.uuid4()), db=db_session)
    u_email = f"syncmiss-{uuid.uuid4().hex[:6]}@example.com"
    from tests.test_auth import _bind_tenant as bt
    from tests.test_auth import _create_user as cu

    u = cu(db_session, u_email, "pw")
    tid = bt(db_session, u)
    repo = DataSourceRepository(db_session)
    src = repo.create(
        tenant_id=tid,
        name="BadType",
        connector_type="file",
        config={},
        created_by_user_id=u.id,
        secret=None,
    )
    src.connector_type = "nope"
    db_session.add(src)
    db_session.commit()
    run = repo.create_sync_run(tenant_id=tid, data_source_id=src.id, correlation_id="c")
    run_data_source_sync(str(run.id), db=db_session)
    again = repo.get_sync_run(run.id)
    assert again is not None
    assert again.status == "failed"
