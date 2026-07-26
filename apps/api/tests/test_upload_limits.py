"""API — limites de tamanho e extensões no upload."""

import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from fourpro_api.config import reset_settings_cache
from tests.test_auth import _bind_tenant, _create_user


@pytest.mark.integration
@pytest.mark.api
@pytest.mark.ingestion
@pytest.mark.security
def test_upload_rejects_oversize(client: TestClient, db_session: Session, monkeypatch) -> None:
    monkeypatch.setenv("MAX_UPLOAD_MB", "1")
    reset_settings_cache()
    u = _create_user(db_session, "big@example.com", "secretpass123")
    _bind_tenant(db_session, u, role="analyst")
    token = client.post(
        "/api/v1/auth/login",
        json={"email": "big@example.com", "password": "secretpass123"},
    ).json()["access_token"]
    # > 1 MiB
    payload = b"c\n" + (b"0\n" * 600_000)
    assert len(payload) > 1 * 1024 * 1024
    r = client.post(
        "/api/v1/uploads",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("big.csv", payload, "text/csv")},
    )
    assert r.status_code in (400, 413)
    reset_settings_cache()


@pytest.mark.integration
@pytest.mark.api
@pytest.mark.ingestion
def test_upload_accepts_json(client: TestClient, db_session: Session) -> None:
    u = _create_user(db_session, "jsonup@example.com", "secretpass123")
    tid = _bind_tenant(db_session, u, role="analyst")
    token = client.post(
        "/api/v1/auth/login",
        json={"email": "jsonup@example.com", "password": "secretpass123"},
    ).json()["access_token"]
    body = b'{"rows":[1,2,3]}'
    r = client.post(
        "/api/v1/uploads",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("data.json", body, "application/json")},
    )
    assert r.status_code == 200
    assert r.json()["status"] == "uploaded"
    stored = list((Path(os.environ["UPLOAD_DIR"]) / str(tid)).glob("*"))
    assert stored
