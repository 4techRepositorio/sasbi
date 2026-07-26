"""Governança — erros de promoção e bronze→gold."""

import uuid
from datetime import UTC, datetime
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from fourpro_api.models.ingestion import FileIngestion
from tests.test_auth import _bind_tenant, _create_user


def _row(
    db: Session, tid, path: Path, *, layer: str = "bronze", write: bool = True
) -> FileIngestion:
    if write:
        path.write_text("a,b\n1,2\n", encoding="utf-8")
        size = path.stat().st_size
        storage = str(path)
    else:
        size = 10
        storage = str(path)
    now = datetime.now(tz=UTC)
    row = FileIngestion(
        id=uuid.uuid4(),
        tenant_id=tid,
        original_filename=path.name,
        storage_path=storage,
        content_type="text/csv",
        size_bytes=size,
        status="processed",
        layer=layer,
        created_at=now,
        updated_at=now,
    )
    db.add(row)
    db.commit()
    return row


@pytest.mark.integration
@pytest.mark.api
def test_promote_same_layer_rejected(
    client: TestClient, db_session: Session, tmp_path: Path
) -> None:
    u = _create_user(db_session, "govsame@example.com", "pw")
    tid = _bind_tenant(db_session, u)
    src = _row(db_session, tid, tmp_path / "a.csv", layer="silver")
    token = client.post(
        "/api/v1/auth/login", json={"email": "govsame@example.com", "password": "pw"}
    ).json()["access_token"]
    r = client.post(
        f"/api/v1/datasets/{src.id}/promote",
        headers={"Authorization": f"Bearer {token}"},
        json={"target_layer": "bronze"},
    )
    assert r.status_code == 400


@pytest.mark.integration
@pytest.mark.api
def test_promote_missing_file_conflict(
    client: TestClient, db_session: Session, tmp_path: Path
) -> None:
    u = _create_user(db_session, "govmiss@example.com", "pw")
    tid = _bind_tenant(db_session, u)
    src = _row(db_session, tid, tmp_path / "gone.csv", write=False)
    token = client.post(
        "/api/v1/auth/login", json={"email": "govmiss@example.com", "password": "pw"}
    ).json()["access_token"]
    r = client.post(
        f"/api/v1/datasets/{src.id}/promote",
        headers={"Authorization": f"Bearer {token}"},
        json={"target_layer": "silver"},
    )
    assert r.status_code == 409


@pytest.mark.integration
@pytest.mark.api
def test_promote_bronze_to_gold(client: TestClient, db_session: Session, tmp_path: Path) -> None:
    u = _create_user(db_session, "govgold@example.com", "pw")
    tid = _bind_tenant(db_session, u)
    src = _row(db_session, tid, tmp_path / "b.csv", layer="bronze")
    token = client.post(
        "/api/v1/auth/login", json={"email": "govgold@example.com", "password": "pw"}
    ).json()["access_token"]
    r = client.post(
        f"/api/v1/datasets/{src.id}/promote",
        headers={"Authorization": f"Bearer {token}"},
        json={"target_layer": "gold", "transform_version": "v2"},
    )
    assert r.status_code == 200, r.text
    assert r.json()["layer"] == "gold"
