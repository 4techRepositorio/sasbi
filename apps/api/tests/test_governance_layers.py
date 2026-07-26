"""TICKET-012 — camadas e promoção."""

import uuid
from datetime import UTC, datetime
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from fourpro_api.models.ingestion import FileIngestion
from tests.test_auth import _bind_tenant, _create_user


def _processed(db: Session, tenant_id, path: Path) -> FileIngestion:
    path.write_text("a,b\n1,2\n", encoding="utf-8")
    now = datetime.now(tz=UTC)
    row = FileIngestion(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        original_filename="src.csv",
        storage_path=str(path),
        content_type="text/csv",
        size_bytes=path.stat().st_size,
        status="processed",
        layer="bronze",
        created_at=now,
        updated_at=now,
    )
    db.add(row)
    db.commit()
    return row


def test_promote_bronze_to_silver(client: TestClient, db_session: Session, tmp_path: Path) -> None:
    u = _create_user(db_session, "gov@example.com", "pw")
    tid = _bind_tenant(db_session, u)
    src = _processed(db_session, tid, tmp_path / "src.csv")
    token = client.post(
        "/api/v1/auth/login", json={"email": "gov@example.com", "password": "pw"}
    ).json()["access_token"]
    r = client.post(
        f"/api/v1/datasets/{src.id}/promote",
        headers={"Authorization": f"Bearer {token}"},
        json={"target_layer": "silver", "transform_version": "v1"},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["layer"] == "silver"
    assert body["source_ingestion_id"] == str(src.id)

    catalog = client.get(
        "/api/v1/datasets?layer=silver",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert catalog.status_code == 200
    assert any(i["id"] == body["id"] for i in catalog.json()["items"])


def test_promote_cross_tenant_denied(
    client: TestClient, db_session: Session, tmp_path: Path
) -> None:
    u1 = _create_user(db_session, "g1@example.com", "pw")
    _bind_tenant(db_session, u1)
    u2 = _create_user(db_session, "g2@example.com", "pw")
    t2 = _bind_tenant(db_session, u2)
    src = _processed(db_session, t2, tmp_path / "other.csv")
    token = client.post(
        "/api/v1/auth/login", json={"email": "g1@example.com", "password": "pw"}
    ).json()["access_token"]
    r = client.post(
        f"/api/v1/datasets/{src.id}/promote",
        headers={"Authorization": f"Bearer {token}"},
        json={"target_layer": "silver"},
    )
    assert r.status_code == 404
