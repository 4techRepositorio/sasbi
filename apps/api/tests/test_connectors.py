"""TICKET-015 — fontes e secrets."""

import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from tests.test_auth import _bind_tenant, _create_user


@pytest.fixture(autouse=True)
def _sync_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("INGESTION_SYNC_PARSE_FALLBACK", "1")
    monkeypatch.delenv("REDIS_URL", raising=False)
    os.environ.pop("REDIS_URL", None)


def test_connector_catalog_and_source_no_secret_leak(
    client: TestClient, db_session: Session
) -> None:
    u = _create_user(db_session, "conn@example.com", "pw")
    _bind_tenant(db_session, u)
    token = client.post(
        "/api/v1/auth/login", json={"email": "conn@example.com", "password": "pw"}
    ).json()["access_token"]
    cat = client.get("/api/v1/connectors", headers={"Authorization": f"Bearer {token}"})
    assert cat.status_code == 200
    types = {i["type"] for i in cat.json()["items"]}
    assert types == {"file", "postgres", "rest_json"}

    created = client.post(
        "/api/v1/data-sources",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "PG demo",
            "connector_type": "postgres",
            "config": {"host": "db.example", "database": "d", "table": "sales"},
            "secret": "user:super-secret-password",
        },
    )
    assert created.status_code == 201, created.text
    body = created.json()
    assert body["has_secret"] is True
    assert "secret" not in body
    assert "super-secret" not in created.text

    listed = client.get("/api/v1/data-sources", headers={"Authorization": f"Bearer {token}"})
    assert "super-secret" not in listed.text

    sync = client.post(
        f"/api/v1/data-sources/{body['id']}/sync",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert sync.status_code == 200, sync.text
    assert sync.json()["status"] in ("queued", "processed", "running", "failed")


def test_data_source_tenant_isolation(client: TestClient, db_session: Session) -> None:
    u1 = _create_user(db_session, "c1@example.com", "pw")
    _bind_tenant(db_session, u1)
    u2 = _create_user(db_session, "c2@example.com", "pw")
    _bind_tenant(db_session, u2)
    t1 = client.post(
        "/api/v1/auth/login", json={"email": "c1@example.com", "password": "pw"}
    ).json()["access_token"]
    src = client.post(
        "/api/v1/data-sources",
        headers={"Authorization": f"Bearer {t1}"},
        json={"name": "F", "connector_type": "file", "config": {}},
    ).json()
    t2 = client.post(
        "/api/v1/auth/login", json={"email": "c2@example.com", "password": "pw"}
    ).json()["access_token"]
    r = client.get(
        f"/api/v1/data-sources/{src['id']}",
        headers={"Authorization": f"Bearer {t2}"},
    )
    assert r.status_code == 404
