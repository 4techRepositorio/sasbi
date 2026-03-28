import uuid
from datetime import UTC, datetime

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from fourpro_api.models.ingestion import FileIngestion
from fourpro_api.repositories.ingestion_repository import IngestionRepository

from tests.test_auth import _bind_tenant, _create_user


def test_ingestions_requires_auth(client: TestClient) -> None:
    r = client.get("/api/v1/ingestions")
    assert r.status_code == 401


def test_list_ingestions(client: TestClient, db_session: Session) -> None:
    u = _create_user(db_session, "ing@example.com", "secretpass123")
    tid = _bind_tenant(db_session, u)
    repo = IngestionRepository(db_session)
    repo.create(
        tenant_id=tid,
        original_filename="a.csv",
        storage_path="/tmp/a",
        content_type="text/csv",
        size_bytes=10,
        status="uploaded",
    )
    repo.create(
        tenant_id=tid,
        original_filename="b.csv",
        storage_path="/tmp/b",
        content_type="text/csv",
        size_bytes=20,
        status="processed",
    )
    r_login = client.post(
        "/api/v1/auth/login",
        json={"email": "ing@example.com", "password": "secretpass123"},
    )
    assert r_login.status_code == 200
    token = r_login.json()["access_token"]
    r = client.get("/api/v1/ingestions", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    body = r.json()
    assert len(body) == 2
    names = {x["original_filename"] for x in body}
    assert names == {"a.csv", "b.csv"}
    for row in body:
        assert row["tenant_id"] == str(tid)


def test_list_ingestions_status_filter(client: TestClient, db_session: Session) -> None:
    u = _create_user(db_session, "ing2@example.com", "secretpass123")
    tid = _bind_tenant(db_session, u)
    repo = IngestionRepository(db_session)
    repo.create(
        tenant_id=tid,
        original_filename="only.csv",
        storage_path="/tmp/o",
        content_type=None,
        size_bytes=1,
        status="uploaded",
    )
    repo.create(
        tenant_id=tid,
        original_filename="done.csv",
        storage_path="/tmp/d",
        content_type=None,
        size_bytes=1,
        status="processed",
    )
    token = client.post(
        "/api/v1/auth/login",
        json={"email": "ing2@example.com", "password": "secretpass123"},
    ).json()["access_token"]
    r = client.get(
        "/api/v1/ingestions?status=uploaded",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    body = r.json()
    assert len(body) == 1
    assert body[0]["status"] == "uploaded"
    assert body[0]["original_filename"] == "only.csv"


def test_get_ingestion_detail(client: TestClient, db_session: Session) -> None:
    u = _create_user(db_session, "det@example.com", "pw")
    tid = _bind_tenant(db_session, u)
    repo = IngestionRepository(db_session)
    ing = repo.create(
        tenant_id=tid,
        original_filename="z.csv",
        storage_path="/z",
        content_type=None,
        size_bytes=3,
        status="uploaded",
    )
    token = client.post("/api/v1/auth/login", json={"email": "det@example.com", "password": "pw"}).json()[
        "access_token"
    ]
    r = client.get(
        f"/api/v1/ingestions/{ing.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    assert r.json()["id"] == str(ing.id)
    assert r.json()["original_filename"] == "z.csv"


def test_get_ingestion_other_tenant_returns_404(client: TestClient, db_session: Session) -> None:
    u1 = _create_user(db_session, "g1@example.com", "pw")
    _bind_tenant(db_session, u1)
    u2 = _create_user(db_session, "g2@example.com", "pw")
    t2 = _bind_tenant(db_session, u2)
    repo = IngestionRepository(db_session)
    ing = repo.create(
        tenant_id=t2,
        original_filename="secret.csv",
        storage_path="/s",
        content_type=None,
        size_bytes=1,
        status="uploaded",
    )
    token1 = client.post("/api/v1/auth/login", json={"email": "g1@example.com", "password": "pw"}).json()[
        "access_token"
    ]
    r = client.get(
        f"/api/v1/ingestions/{ing.id}",
        headers={"Authorization": f"Bearer {token1}"},
    )
    assert r.status_code == 404


def test_ingestions_tenant_isolation(client: TestClient, db_session: Session) -> None:
    u1 = _create_user(db_session, "iso1@example.com", "pw")
    t1 = _bind_tenant(db_session, u1)
    u2 = _create_user(db_session, "iso2@example.com", "pw")
    t2 = _bind_tenant(db_session, u2)
    now = datetime.now(tz=UTC)
    db_session.add_all(
        [
            FileIngestion(
                id=uuid.uuid4(),
                tenant_id=t1,
                original_filename="t1.csv",
                storage_path="/x/1",
                content_type=None,
                size_bytes=1,
                status="uploaded",
                created_at=now,
                updated_at=now,
            ),
            FileIngestion(
                id=uuid.uuid4(),
                tenant_id=t2,
                original_filename="other-tenant.csv",
                storage_path="/x/2",
                content_type=None,
                size_bytes=1,
                status="uploaded",
                created_at=now,
                updated_at=now,
            ),
        ],
    )
    db_session.commit()
    token = client.post(
        "/api/v1/auth/login",
        json={"email": "iso1@example.com", "password": "pw"},
    ).json()["access_token"]
    r = client.get("/api/v1/ingestions", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert len(r.json()) == 1
    assert r.json()[0]["original_filename"] == "t1.csv"
