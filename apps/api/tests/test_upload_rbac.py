"""TICKET-005/006 — RBAC no upload e validação de conteúdo."""

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from tests.test_auth import _bind_tenant, _create_user


def _token_for(client: TestClient, db_session: Session, email: str, pwd: str, role: str = "admin") -> str:
    u = _create_user(db_session, email, pwd)
    _bind_tenant(db_session, u, role=role)
    r = client.post("/api/v1/auth/login", json={"email": email, "password": pwd})
    assert r.status_code == 200
    return r.json()["access_token"]


def test_upload_forbidden_for_consumer(client: TestClient, db_session: Session) -> None:
    token = _token_for(client, db_session, "cons@example.com", "pw", role="consumer")
    files = {"file": ("x.csv", b"a,b\n1,1\n", "text/csv")}
    r = client.post(
        "/api/v1/uploads",
        headers={"Authorization": f"Bearer {token}"},
        files=files,
    )
    assert r.status_code == 403


def test_upload_rejects_content_spoofing_csv(client: TestClient, db_session: Session) -> None:
    token = _token_for(client, db_session, "adm@example.com", "pw", role="admin")
    files = {"file": ("fake.csv", b"\xd0\xcf\x11\xe0not a csv", "text/csv")}
    r = client.post(
        "/api/v1/uploads",
        headers={"Authorization": f"Bearer {token}"},
        files=files,
    )
    assert r.status_code == 400


def test_upload_accepts_valid_csv(client: TestClient, db_session: Session) -> None:
    token = _token_for(client, db_session, "up@example.com", "pw", role="analyst")
    files = {"file": ("data.csv", b"col\n1\n", "text/csv")}
    r = client.post(
        "/api/v1/uploads",
        headers={"Authorization": f"Bearer {token}"},
        files=files,
    )
    assert r.status_code == 200
    body = r.json()
    assert body.get("status") == "uploaded"
    assert "id" in body
