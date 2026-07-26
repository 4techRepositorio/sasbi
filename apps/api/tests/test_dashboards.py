"""TICKET-011 — dashboards multitenant."""

import uuid
from datetime import UTC, datetime

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from fourpro_api.models.ingestion import FileIngestion
from tests.test_auth import _bind_tenant, _create_user


def test_dashboard_crud_and_isolation(client: TestClient, db_session: Session) -> None:
    u1 = _create_user(db_session, "dsha@example.com", "pw")
    t1 = _bind_tenant(db_session, u1)
    u2 = _create_user(db_session, "dshb@example.com", "pw")
    _bind_tenant(db_session, u2)
    now = datetime.now(tz=UTC)
    ds = FileIngestion(
        id=uuid.uuid4(),
        tenant_id=t1,
        original_filename="kpi.csv",
        storage_path="/tmp/kpi.csv",
        size_bytes=3,
        status="processed",
        layer="bronze",
        created_at=now,
        updated_at=now,
    )
    db_session.add(ds)
    db_session.commit()

    tok_a = client.post(
        "/api/v1/auth/login", json={"email": "dsha@example.com", "password": "pw"}
    ).json()["access_token"]
    created = client.post(
        "/api/v1/dashboards",
        headers={"Authorization": f"Bearer {tok_a}"},
        json={
            "title": "Vendas",
            "widgets": [
                {
                    "widget_type": "kpi",
                    "title": "Linhas",
                    "dataset_id": str(ds.id),
                    "config": {},
                    "position": {"x": 0, "y": 0},
                }
            ],
        },
    )
    assert created.status_code == 201, created.text
    dash_id = created.json()["id"]
    assert created.json()["widgets"][0]["dataset_available"] is True

    tok_b = client.post(
        "/api/v1/auth/login", json={"email": "dshb@example.com", "password": "pw"}
    ).json()["access_token"]
    denied = client.get(
        f"/api/v1/dashboards/{dash_id}",
        headers={"Authorization": f"Bearer {tok_b}"},
    )
    assert denied.status_code == 404

    export = client.get(
        f"/api/v1/dashboards/{dash_id}/export",
        headers={"Authorization": f"Bearer {tok_a}"},
    )
    assert export.status_code == 200
    assert export.json()["format"] == "json_snapshot"


def test_consumer_cannot_create_dashboard(client: TestClient, db_session: Session) -> None:
    u = _create_user(db_session, "consdash@example.com", "pw")
    _bind_tenant(db_session, u, role="consumer")
    token = client.post(
        "/api/v1/auth/login", json={"email": "consdash@example.com", "password": "pw"}
    ).json()["access_token"]
    r = client.post(
        "/api/v1/dashboards",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "X"},
    )
    assert r.status_code == 403
