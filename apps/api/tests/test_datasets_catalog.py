"""TICKET-009 — catálogo paginado e isolado por tenant."""

from datetime import UTC, datetime
import uuid

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from fourpro_api.models.ingestion import FileIngestion

from tests.test_auth import _bind_tenant, _create_user


def test_datasets_pagination_shape(client: TestClient, db_session: Session) -> None:
    u = _create_user(db_session, "cat@example.com", "pw")
    tid = _bind_tenant(db_session, u)
    now = datetime.now(tz=UTC)
    db_session.add(
        FileIngestion(
            id=uuid.uuid4(),
            tenant_id=tid,
            original_filename="done.csv",
            storage_path="/tmp/x",
            content_type=None,
            size_bytes=10,
            status="processed",
            result_summary="ok",
            created_at=now,
            updated_at=now,
        ),
    )
    db_session.commit()
    token = client.post("/api/v1/auth/login", json={"email": "cat@example.com", "password": "pw"}).json()[
        "access_token"
    ]
    r = client.get(
        "/api/v1/datasets?limit=5&offset=0",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["total"] >= 1
    assert len(data["items"]) >= 1
    assert data["limit"] == 5
    assert data["offset"] == 0


def test_datasets_only_own_tenant(client: TestClient, db_session: Session) -> None:
    u1 = _create_user(db_session, "d1@example.com", "pw")
    t1 = _bind_tenant(db_session, u1)
    u2 = _create_user(db_session, "d2@example.com", "pw")
    t2 = _bind_tenant(db_session, u2)
    now = datetime.now(tz=UTC)
    db_session.add(
        FileIngestion(
            id=uuid.uuid4(),
            tenant_id=t2,
            original_filename="other.csv",
            storage_path="/z",
            content_type=None,
            size_bytes=1,
            status="processed",
            created_at=now,
            updated_at=now,
        ),
    )
    db_session.commit()
    token = client.post("/api/v1/auth/login", json={"email": "d1@example.com", "password": "pw"}).json()[
        "access_token"
    ]
    r = client.get("/api/v1/datasets", headers={"Authorization": f"Bearer {token}"})
    names = [x["original_filename"] for x in r.json()["items"]]
    assert "other.csv" not in names
