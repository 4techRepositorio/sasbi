"""Reprocessamento de ingestões — RBAC, isolamento por tenant e conflitos."""

import tempfile
import uuid
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from fourpro_api.repositories.ingestion_repository import IngestionRepository
from tests.test_auth import _bind_tenant, _create_user


def _csv_path() -> Path:
    p = Path(tempfile.gettempdir()) / f"reprocess_{uuid.uuid4().hex}.csv"
    p.write_text("x,y\n1,1\n", encoding="utf-8")
    return p


def test_reprocess_analyst_clears_errors_and_sets_uploaded(
    client: TestClient, db_session: Session
) -> None:
    u = _create_user(db_session, "repr@example.com", "secretpass123")
    tid = _bind_tenant(db_session, u, role="analyst")
    tmp = _csv_path()
    repo = IngestionRepository(db_session)
    ing = repo.create(
        tenant_id=tid,
        original_filename="x.csv",
        storage_path=str(tmp.resolve()),
        content_type="text/csv",
        size_bytes=tmp.stat().st_size,
        status="failed",
    )
    repo.update(ing, friendly_error="antigo", technical_log="stack")

    tok = client.post(
        "/api/v1/auth/login",
        json={"email": "repr@example.com", "password": "secretpass123"},
    ).json()["access_token"]
    r = client.post(
        f"/api/v1/ingestions/{ing.id}/reprocess",
        headers={"Authorization": f"Bearer {tok}"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "uploaded"
    assert body["friendly_error"] is None
    assert body["result_summary"] is None


def test_reprocess_consumer_forbidden(client: TestClient, db_session: Session) -> None:
    u = _create_user(db_session, "cons@example.com", "secretpass123")
    tid = _bind_tenant(db_session, u, role="consumer")
    tmp = _csv_path()
    repo = IngestionRepository(db_session)
    ing = repo.create(
        tenant_id=tid,
        original_filename="c.csv",
        storage_path=str(tmp.resolve()),
        content_type="text/csv",
        size_bytes=tmp.stat().st_size,
        status="processed",
    )
    tok = client.post(
        "/api/v1/auth/login",
        json={"email": "cons@example.com", "password": "secretpass123"},
    ).json()["access_token"]
    r = client.post(
        f"/api/v1/ingestions/{ing.id}/reprocess",
        headers={"Authorization": f"Bearer {tok}"},
    )
    assert r.status_code == 403
    assert r.json()["detail"] == "Permissão insuficiente"


def test_reprocess_while_validating_returns_409(client: TestClient, db_session: Session) -> None:
    u = _create_user(db_session, "val@example.com", "secretpass123")
    tid = _bind_tenant(db_session, u, role="admin")
    tmp = _csv_path()
    repo = IngestionRepository(db_session)
    ing = repo.create(
        tenant_id=tid,
        original_filename="v.csv",
        storage_path=str(tmp.resolve()),
        content_type="text/csv",
        size_bytes=tmp.stat().st_size,
        status="validating",
    )
    tok = client.post(
        "/api/v1/auth/login",
        json={"email": "val@example.com", "password": "secretpass123"},
    ).json()["access_token"]
    r = client.post(
        f"/api/v1/ingestions/{ing.id}/reprocess",
        headers={"Authorization": f"Bearer {tok}"},
    )
    assert r.status_code == 409


def test_reprocess_other_tenant_returns_404(client: TestClient, db_session: Session) -> None:
    u1 = _create_user(db_session, "iso_a@example.com", "pw")
    _bind_tenant(db_session, u1, role="analyst")
    u2 = _create_user(db_session, "iso_b@example.com", "pw")
    t2 = _bind_tenant(db_session, u2, role="admin")
    tmp = _csv_path()
    repo = IngestionRepository(db_session)
    ing = repo.create(
        tenant_id=t2,
        original_filename="secret.csv",
        storage_path=str(tmp.resolve()),
        content_type="text/csv",
        size_bytes=tmp.stat().st_size,
        status="failed",
    )
    tok = client.post(
        "/api/v1/auth/login",
        json={"email": "iso_a@example.com", "password": "pw"},
    ).json()["access_token"]
    r = client.post(
        f"/api/v1/ingestions/{ing.id}/reprocess",
        headers={"Authorization": f"Bearer {tok}"},
    )
    assert r.status_code == 404
