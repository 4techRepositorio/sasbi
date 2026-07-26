"""TICKET-017 — publish Desktop."""

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from tests.test_auth import _bind_tenant, _create_user


def test_desktop_publish_dataset_and_dashboard(
    client: TestClient, db_session: Session
) -> None:
    u = _create_user(db_session, "desk@example.com", "pw")
    _bind_tenant(db_session, u)
    token = client.post(
        "/api/v1/auth/login", json={"email": "desk@example.com", "password": "pw"}
    ).json()["access_token"]
    ds = client.post(
        "/api/v1/desktop/publish/dataset",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "FromDesktop",
            "rows": [{"a": 1}, {"a": 2}],
            "layer": "gold",
        },
    )
    assert ds.status_code == 201, ds.text
    assert ds.json()["layer"] == "gold"
    catalog = client.get("/api/v1/datasets", headers={"Authorization": f"Bearer {token}"})
    assert any(i["id"] == ds.json()["dataset_id"] for i in catalog.json()["items"])

    dash = client.post(
        "/api/v1/desktop/publish/dashboard",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Desk Dash",
            "widgets": [
                {
                    "widget_type": "kpi",
                    "title": "N",
                    "dataset_id": ds.json()["dataset_id"],
                }
            ],
        },
    )
    assert dash.status_code == 201, dash.text
    got = client.get(
        f"/api/v1/dashboards/{dash.json()['dashboard_id']}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert got.status_code == 200
