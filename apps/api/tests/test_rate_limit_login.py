"""Segurança — rate limit no login (429)."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from fourpro_api.config import reset_settings_cache
from fourpro_api.db.session import get_db
from fourpro_api.limiter import limiter
from fourpro_api.main import create_app
from tests.test_auth import _bind_tenant, _create_user


@pytest.fixture
def rate_limited_client(db_session: Session, monkeypatch) -> TestClient:
    monkeypatch.setenv("LOGIN_RATE_LIMIT", "3/minute")
    reset_settings_cache()
    prev = limiter.enabled
    limiter.enabled = True
    app = create_app()

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
    limiter.enabled = prev
    reset_settings_cache()


@pytest.mark.integration
@pytest.mark.api
@pytest.mark.security
@pytest.mark.auth
def test_login_rate_limit_returns_429(rate_limited_client: TestClient, db_session: Session) -> None:
    u = _create_user(db_session, "rl@example.com", "secretpass123")
    _bind_tenant(db_session, u)
    payload = {"email": "rl@example.com", "password": "wrong-password"}
    codes = []
    for _ in range(5):
        codes.append(rate_limited_client.post("/api/v1/auth/login", json=payload).status_code)
    assert 429 in codes, f"esperado 429 após burst; códigos={codes}"
