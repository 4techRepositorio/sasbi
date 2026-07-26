"""API — list/patch/delete dashboards (cobertura BI)."""

import uuid
from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from fourpro_api.models.ingestion import FileIngestion
from tests.test_auth import _bind_tenant, _create_user


def _dataset(db: Session, tenant_id) -> FileIngestion:
    now = datetime.now(tz=UTC)
    ds = FileIngestion(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        original_filename="kpi.csv",
        storage_path="/tmp/kpi.csv",
        size_bytes=3,
        status="processed",
        layer="bronze",
        created_at=now,
        updated_at=now,
    )
    db.add(ds)
    db.commit()
    return ds


@pytest.mark.integration
@pytest.mark.api
def test_dashboard_list_patch_delete(client: TestClient, db_session: Session) -> None:
    u = _create_user(db_session, "dashcrud@example.com", "pw")
    tid = _bind_tenant(db_session, u)
    ds = _dataset(db_session, tid)
    token = client.post(
        "/api/v1/auth/login", json={"email": "dashcrud@example.com", "password": "pw"}
    ).json()["access_token"]
    h = {"Authorization": f"Bearer {token}"}

    created = client.post(
        "/api/v1/dashboards",
        headers=h,
        json={
            "title": "Ops",
            "description": "d1",
            "widgets": [
                {
                    "widget_type": "kpi",
                    "title": "A",
                    "dataset_id": str(ds.id),
                    "config": {},
                    "position": {"x": 0, "y": 0},
                }
            ],
        },
    )
    assert created.status_code == 201
    dash_id = created.json()["id"]

    listed = client.get("/api/v1/dashboards", headers=h)
    assert listed.status_code == 200
    assert any(i["id"] == dash_id for i in listed.json()["items"])

    got = client.get(f"/api/v1/dashboards/{dash_id}", headers=h)
    assert got.status_code == 200
    assert got.json()["title"] == "Ops"

    patched = client.patch(
        f"/api/v1/dashboards/{dash_id}",
        headers=h,
        json={
            "title": "Ops v2",
            "description": "d2",
            "layout_json": {"cols": 12},
            "widgets": [
                {
                    "widget_type": "table",
                    "title": "B",
                    "dataset_id": None,
                    "config": {"page": 1},
                    "position": {"x": 1, "y": 0},
                }
            ],
        },
    )
    assert patched.status_code == 200, patched.text
    assert patched.json()["title"] == "Ops v2"
    assert len(patched.json()["widgets"]) == 1
    assert patched.json()["widgets"][0]["dataset_available"] is True

    assert client.delete(f"/api/v1/dashboards/{dash_id}", headers=h).status_code == 204
    assert client.get(f"/api/v1/dashboards/{dash_id}", headers=h).status_code == 404
    assert (
        client.patch(f"/api/v1/dashboards/{dash_id}", headers=h, json={"title": "x"}).status_code
        == 404
    )
    assert client.delete(f"/api/v1/dashboards/{dash_id}", headers=h).status_code == 404
    assert client.get(f"/api/v1/dashboards/{dash_id}/export", headers=h).status_code == 404
