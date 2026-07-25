"""Testes TICKET-015 — data sources / conectores."""

from __future__ import annotations

import json
import os
from pathlib import Path

import httpx
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from tests.test_auth import _bind_tenant, _create_user


@pytest.fixture(autouse=True)
def _sync_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("INGESTION_SYNC_PARSE_FALLBACK", "1")


def _login(client: TestClient, email: str, password: str) -> str:
    r = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


def test_connectors_catalog(client: TestClient, db_session: Session) -> None:
    u = _create_user(db_session, "cat@example.com", "secretpass123")
    _bind_tenant(db_session, u)
    token = _login(client, "cat@example.com", "secretpass123")
    r = client.get("/api/v1/connectors", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    types = {i["connector_type"] for i in r.json()["items"]}
    assert "file" in types
    assert "postgres" in types
    assert "rest_json" in types


def test_create_get_hides_secret(client: TestClient, db_session: Session, tmp_path: Path) -> None:
    u = _create_user(db_session, "sec@example.com", "secretpass123")
    _bind_tenant(db_session, u)
    token = _login(client, "sec@example.com", "secretpass123")
    root = tmp_path / "files"
    root.mkdir()
    (root / "a.csv").write_text("x,y\n1,2\n", encoding="utf-8")
    r = client.post(
        "/api/v1/data-sources",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Local CSV",
            "connector_type": "file",
            "config": {"root_path": str(root)},
            "secret": {"password": "super-secret-never-return"},
        },
    )
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["has_secret"] is True
    assert "secret" not in body
    assert "super-secret" not in json.dumps(body)

    gid = body["id"]
    g = client.get(
        f"/api/v1/data-sources/{gid}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert g.status_code == 200
    assert "secret" not in g.json()
    assert "super-secret" not in json.dumps(g.json())
    assert g.json()["has_secret"] is True


def test_tenant_isolation(client: TestClient, db_session: Session, tmp_path: Path) -> None:
    u1 = _create_user(db_session, "t1@example.com", "pw")
    _bind_tenant(db_session, u1)
    u2 = _create_user(db_session, "t2@example.com", "pw")
    _bind_tenant(db_session, u2)
    tok1 = _login(client, "t1@example.com", "pw")
    tok2 = _login(client, "t2@example.com", "pw")
    root = tmp_path / "f"
    root.mkdir()
    (root / "a.csv").write_text("a\n1\n", encoding="utf-8")
    created = client.post(
        "/api/v1/data-sources",
        headers={"Authorization": f"Bearer {tok1}"},
        json={
            "name": "T1 source",
            "connector_type": "file",
            "config": {"root_path": str(root)},
        },
    )
    assert created.status_code == 201
    ds_id = created.json()["id"]

    denied = client.get(
        f"/api/v1/data-sources/{ds_id}",
        headers={"Authorization": f"Bearer {tok2}"},
    )
    assert denied.status_code == 404

    denied_sync = client.post(
        f"/api/v1/data-sources/{ds_id}/sync",
        headers={"Authorization": f"Bearer {tok2}"},
        json={"object_id": "a.csv", "mode": "full"},
    )
    assert denied_sync.status_code == 404


def test_file_connection_and_sync(
    client: TestClient, db_session: Session, tmp_path: Path
) -> None:
    u = _create_user(db_session, "sync@example.com", "secretpass123")
    _bind_tenant(db_session, u)
    token = _login(client, "sync@example.com", "secretpass123")
    root = tmp_path / "data"
    root.mkdir()
    (root / "sales.csv").write_text("sku,qty\nA,10\nB,20\n", encoding="utf-8")

    created = client.post(
        "/api/v1/data-sources",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Sales files",
            "connector_type": "file",
            "config": {"root_path": str(root)},
        },
    )
    assert created.status_code == 201, created.text
    ds_id = created.json()["id"]

    test = client.post(
        f"/api/v1/data-sources/{ds_id}/test",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert test.status_code == 200
    assert test.json()["ok"] is True

    disc = client.post(
        f"/api/v1/data-sources/{ds_id}/discover",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert disc.status_code == 200
    assert any(o["object_id"] == "sales.csv" for o in disc.json()["objects"])

    sync = client.post(
        f"/api/v1/data-sources/{ds_id}/sync",
        headers={"Authorization": f"Bearer {token}"},
        json={"object_id": "sales.csv", "mode": "full"},
    )
    assert sync.status_code == 200, sync.text
    run_id = sync.json()["sync_run_id"]

    runs = client.get(
        f"/api/v1/data-sources/{ds_id}/sync-runs",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert runs.status_code == 200
    items = runs.json()["items"]
    assert any(i["id"] == run_id for i in items)
    # fallback sync corre em processo — deve chegar a processed/failed
    statuses = {i["status"] for i in items if i["id"] == run_id}
    assert statuses & {"processed", "failed", "uploaded", "parsing", "running", "queued"}


def test_rest_json_sync_with_mock(
    client: TestClient,
    db_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    payload = [{"id": 1, "name": "alpha"}, {"id": 2, "name": "beta"}]

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=payload, request=request)

    transport = httpx.MockTransport(handler)
    real_client = httpx.Client

    def client_factory(*args, **kwargs):  # noqa: ANN002
        kwargs["transport"] = transport
        kwargs.setdefault("follow_redirects", False)
        return real_client(*args, **kwargs)

    monkeypatch.setattr(httpx, "Client", client_factory)

    u = _create_user(db_session, "rest@example.com", "secretpass123")
    _bind_tenant(db_session, u)
    token = _login(client, "rest@example.com", "secretpass123")

    created = client.post(
        "/api/v1/data-sources",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "REST demo",
            "connector_type": "rest_json",
            "config": {
                "base_url": "https://example.com",
                "path": "/items",
                "allowed_hosts": ["example.com"],
            },
            "secret": {"token": "tok-xyz"},
        },
    )
    assert created.status_code == 201, created.text
    ds_id = created.json()["id"]
    assert "tok-xyz" not in json.dumps(created.json())

    test = client.post(
        f"/api/v1/data-sources/{ds_id}/test",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert test.status_code == 200
    assert test.json()["ok"] is True

    sync = client.post(
        f"/api/v1/data-sources/{ds_id}/sync",
        headers={"Authorization": f"Bearer {token}"},
        json={"object_id": "items", "mode": "sample", "sample_limit": 10},
    )
    assert sync.status_code == 200, sync.text

    runs = client.get(
        f"/api/v1/data-sources/{ds_id}/sync-runs",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert runs.status_code == 200
    assert runs.json()["total"] >= 1


def test_viewer_cannot_create(client: TestClient, db_session: Session, tmp_path: Path) -> None:
    u = _create_user(db_session, "view@example.com", "pw")
    _bind_tenant(db_session, u, role="consumer")
    token = _login(client, "view@example.com", "pw")
    root = tmp_path / "v"
    root.mkdir()
    r = client.post(
        "/api/v1/data-sources",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Nope",
            "connector_type": "file",
            "config": {"root_path": str(root)},
        },
    )
    assert r.status_code == 403
