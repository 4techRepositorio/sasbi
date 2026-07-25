"""TICKET-016 / TICKET-011 — semantic layer, query, dashboards, desktop publish."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from fourpro_api.models.ingestion import FileIngestion
from tests.test_auth import _bind_tenant, _create_user


def _token(client: TestClient, email: str, password: str = "pw") -> str:
    return client.post("/api/v1/auth/login", json={"email": email, "password": password}).json()[
        "access_token"
    ]


def _processed_dataset(
    db: Session,
    tenant_id: uuid.UUID,
    *,
    rows: list[dict] | None = None,
) -> FileIngestion:
    now = datetime.now(tz=UTC)
    ing = FileIngestion(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        original_filename="sales.csv",
        storage_path="/tmp/missing-ok.csv",
        content_type="text/csv",
        size_bytes=32,
        status="processed",
        result_summary="csv_rows_stored=3",
        parsed_rows_json=rows
        or [
            {"region": "Norte", "amount": 10},
            {"region": "Norte", "amount": 20},
            {"region": "Sul", "amount": 5},
        ],
        created_at=now,
        updated_at=now,
    )
    db.add(ing)
    db.commit()
    db.refresh(ing)
    return ing


def test_semantic_crud_tenant_isolation(client: TestClient, db_session: Session) -> None:
    u1 = _create_user(db_session, "sem1@example.com", "pw")
    t1 = _bind_tenant(db_session, u1, role="admin")
    u2 = _create_user(db_session, "sem2@example.com", "pw")
    t2 = _bind_tenant(db_session, u2, role="admin")
    ds1 = _processed_dataset(db_session, t1)
    ds2 = _processed_dataset(db_session, t2)

    tok1 = _token(client, "sem1@example.com")
    tok2 = _token(client, "sem2@example.com")

    created = client.post(
        "/api/v1/semantic-models",
        headers={"Authorization": f"Bearer {tok1}"},
        json={
            "name": "Sales model",
            "dataset_id": str(ds1.id),
            "fields": [
                {
                    "name": "region",
                    "source_column": "region",
                    "role": "dimension",
                    "data_type": "string",
                },
                {
                    "name": "amount",
                    "source_column": "amount",
                    "role": "measure",
                    "data_type": "number",
                },
            ],
        },
    )
    assert created.status_code == 201, created.text
    model_id = created.json()["id"]

    # Tenant 2 cannot read tenant 1 model
    denied = client.get(
        f"/api/v1/semantic-models/{model_id}",
        headers={"Authorization": f"Bearer {tok2}"},
    )
    assert denied.status_code == 404

    listed = client.get(
        "/api/v1/semantic-models",
        headers={"Authorization": f"Bearer {tok2}"},
    )
    assert listed.status_code == 200
    assert all(i["id"] != model_id for i in listed.json()["items"])

    # Cannot bind other tenant's dataset
    cross = client.post(
        "/api/v1/semantic-models",
        headers={"Authorization": f"Bearer {tok1}"},
        json={"name": "bad", "dataset_id": str(ds2.id), "fields": []},
    )
    assert cross.status_code == 404


def test_query_aggregation_happy_path(client: TestClient, db_session: Session) -> None:
    u = _create_user(db_session, "qry@example.com", "pw")
    tid = _bind_tenant(db_session, u, role="analyst")
    ds = _processed_dataset(db_session, tid)
    tok = _token(client, "qry@example.com")

    model = client.post(
        "/api/v1/semantic-models",
        headers={"Authorization": f"Bearer {tok}"},
        json={
            "name": "Agg",
            "dataset_id": str(ds.id),
            "fields": [
                {
                    "name": "region",
                    "source_column": "region",
                    "role": "dimension",
                    "data_type": "string",
                },
                {
                    "name": "amount",
                    "source_column": "amount",
                    "role": "measure",
                    "data_type": "number",
                },
            ],
        },
    ).json()

    r = client.post(
        "/api/v1/query",
        headers={"Authorization": f"Bearer {tok}"},
        json={
            "semantic_model_id": model["id"],
            "dimensions": ["region"],
            "measures": [{"field": "amount", "op": "sum", "alias": "total"}],
            "limit": 100,
        },
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["row_count"] == 2
    by_region = {row["region"]: row["total"] for row in body["rows"]}
    assert by_region["Norte"] == 30
    assert by_region["Sul"] == 5


def test_query_cross_tenant_denied(client: TestClient, db_session: Session) -> None:
    u1 = _create_user(db_session, "qx1@example.com", "pw")
    t1 = _bind_tenant(db_session, u1, role="admin")
    u2 = _create_user(db_session, "qx2@example.com", "pw")
    _bind_tenant(db_session, u2, role="admin")
    ds = _processed_dataset(db_session, t1)
    tok1 = _token(client, "qx1@example.com")
    tok2 = _token(client, "qx2@example.com")

    model_id = client.post(
        "/api/v1/semantic-models",
        headers={"Authorization": f"Bearer {tok1}"},
        json={
            "name": "Private",
            "dataset_id": str(ds.id),
            "fields": [
                {
                    "name": "amount",
                    "source_column": "amount",
                    "role": "measure",
                    "data_type": "number",
                },
            ],
        },
    ).json()["id"]

    denied = client.post(
        "/api/v1/query",
        headers={"Authorization": f"Bearer {tok2}"},
        json={
            "semantic_model_id": model_id,
            "measures": [{"field": "amount", "op": "sum"}],
        },
    )
    assert denied.status_code == 404


def test_dashboard_publish(client: TestClient, db_session: Session) -> None:
    u = _create_user(db_session, "dash@example.com", "pw")
    _bind_tenant(db_session, u, role="admin")
    tok = _token(client, "dash@example.com")

    created = client.post(
        "/api/v1/dashboards",
        headers={"Authorization": f"Bearer {tok}"},
        json={
            "name": "Overview",
            "description": "KPI board",
            "layout": {
                "version": 1,
                "columns": 12,
                "widgets": [
                    {
                        "id": "w1",
                        "type": "kpi",
                        "title": "Total",
                        "x": 0,
                        "y": 0,
                        "w": 3,
                        "h": 2,
                    }
                ],
            },
        },
    )
    assert created.status_code == 201, created.text
    dash_id = created.json()["id"]
    assert created.json()["status"] == "draft"
    assert created.json()["version"] == 1

    pub = client.post(
        f"/api/v1/dashboards/{dash_id}/publish",
        headers={"Authorization": f"Bearer {tok}"},
    )
    assert pub.status_code == 200, pub.text
    assert pub.json()["status"] == "published"
    assert pub.json()["version"] == 1
    assert pub.json()["published_at"]

    again = client.get(
        f"/api/v1/dashboards/{dash_id}",
        headers={"Authorization": f"Bearer {tok}"},
    )
    assert again.json()["status"] == "published"

    # Re-publish bumps version and keeps snapshot history
    pub2 = client.post(
        f"/api/v1/dashboards/{dash_id}/publish",
        headers={"Authorization": f"Bearer {tok}"},
    )
    assert pub2.status_code == 200
    assert pub2.json()["version"] == 2


def test_desktop_session_and_publish_stubs(client: TestClient, db_session: Session) -> None:
    u = _create_user(db_session, "desk@example.com", "pw")
    _bind_tenant(db_session, u, role="admin")
    tok = _token(client, "desk@example.com")
    headers = {"Authorization": f"Bearer {tok}"}

    session = client.get("/api/v1/desktop/session", headers=headers)
    assert session.status_code == 200
    assert session.json()["tenant_id"]
    assert "semantic-query" in session.json()["features"]

    ds = client.post(
        "/api/v1/desktop/publish-dataset",
        headers=headers,
        json={"name": "From desktop"},
    )
    assert ds.status_code == 200
    assert ds.json()["status"] == "failed"
    assert "fonte de dados" in ds.json()["message"].lower() or "data_source" in ds.json()[
        "message"
    ].lower() or "conectores" in ds.json()["message"].lower()

    dash = client.post(
        "/api/v1/desktop/publish-dashboard",
        headers=headers,
        json={
            "name": "Desktop board",
            "layout": {"version": 1, "columns": 12, "widgets": []},
            "publish": True,
        },
    )
    assert dash.status_code == 200, dash.text
    assert dash.json()["status"] == "published"
    assert dash.json()["dashboard_id"]


def test_parse_job_stores_parsed_rows(tmp_path, db_session: Session) -> None:
    from fourpro_api.jobs.ingestion_parse import run_ingestion_parse
    from fourpro_api.repositories.ingestion_repository import IngestionRepository

    u = _create_user(db_session, "parse2@example.com", "pw")
    tid = _bind_tenant(db_session, u)
    f = tmp_path / "sample.csv"
    f.write_text("region,amount\nNorte,10\nSul,5\n", encoding="utf-8")
    repo = IngestionRepository(db_session)
    ing = repo.create(
        tenant_id=tid,
        original_filename="sample.csv",
        storage_path=str(f.resolve()),
        content_type="text/csv",
        size_bytes=f.stat().st_size,
        status="uploaded",
    )
    run_ingestion_parse(str(ing.id), db=db_session)
    again = repo.get_by_id(ing.id)
    assert again is not None
    assert again.status == "processed"
    assert again.parsed_rows_json is not None
    assert len(again.parsed_rows_json) == 2
    assert again.parsed_rows_json[0]["region"] == "Norte"
