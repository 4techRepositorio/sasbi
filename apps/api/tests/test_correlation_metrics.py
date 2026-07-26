"""TICKET-013 — correlation ID e métricas."""

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from tests.test_auth import _bind_tenant, _create_user


def test_health_returns_request_id(client: TestClient) -> None:
    r = client.get("/api/v1/health")
    assert r.status_code == 200
    assert "X-Request-ID" in r.headers
    assert len(r.headers["X-Request-ID"]) == 36


def test_metrics_endpoint(client: TestClient) -> None:
    client.get("/api/v1/health")
    r = client.get("/api/v1/metrics")
    assert r.status_code == 200
    assert "http_requests_total" in r.text


def test_propagates_incoming_request_id(client: TestClient, db_session: Session) -> None:
    u = _create_user(db_session, "cid@example.com", "pw")
    _bind_tenant(db_session, u)
    fixed = "11111111-1111-1111-1111-111111111111"
    r = client.post(
        "/api/v1/auth/login",
        json={"email": "cid@example.com", "password": "pw"},
        headers={"X-Request-ID": fixed},
    )
    assert r.status_code == 200
    assert r.headers["X-Request-ID"] == fixed
