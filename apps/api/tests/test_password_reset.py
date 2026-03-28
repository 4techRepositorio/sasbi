"""TICKET-002 — recuperação de senha."""

from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from fourpro_api.core.security import hash_refresh_token, verify_password
from fourpro_api.models.password_reset import PasswordResetToken

from tests.test_auth import _create_user


def test_forgot_password_unknown_email_still_200(client: TestClient) -> None:
    r = client.post("/api/v1/auth/forgot-password", json={"email": "nope@example.com"})
    assert r.status_code == 200
    assert "detail" in r.json()


def test_reset_password_success(client: TestClient, db_session: Session, monkeypatch) -> None:
    monkeypatch.setattr(
        "fourpro_api.services.password_reset_service.secrets.token_urlsafe",
        lambda _n: "fixed_test_token_aaaaaaaa",
    )
    u = _create_user(db_session, "reset@example.com", "oldpassword123")
    client.post("/api/v1/auth/forgot-password", json={"email": "reset@example.com"})
    r = client.post(
        "/api/v1/auth/reset-password",
        json={"token": "fixed_test_token_aaaaaaaa", "new_password": "newpassword12345"},
    )
    assert r.status_code == 200
    db_session.refresh(u)
    assert verify_password("newpassword12345", u.password_hash)


def test_reset_password_invalid_token(client: TestClient) -> None:
    r = client.post(
        "/api/v1/auth/reset-password",
        json={"token": "not-a-valid-token-value-at-all", "new_password": "xpassword12345"},
    )
    assert r.status_code == 400


def test_reset_password_token_single_use(client: TestClient, db_session: Session, monkeypatch) -> None:
    monkeypatch.setattr(
        "fourpro_api.services.password_reset_service.secrets.token_urlsafe",
        lambda _n: "second_use_tokenbbbbbbb",
    )
    _create_user(db_session, "two@example.com", "pw")
    client.post("/api/v1/auth/forgot-password", json={"email": "two@example.com"})
    r1 = client.post(
        "/api/v1/auth/reset-password",
        json={"token": "second_use_tokenbbbbbbb", "new_password": "newpass123456"},
    )
    assert r1.status_code == 200
    r2 = client.post(
        "/api/v1/auth/reset-password",
        json={"token": "second_use_tokenbbbbbbb", "new_password": "otherpass123456"},
    )
    assert r2.status_code == 400


def test_reset_password_expired_token(client: TestClient, db_session: Session) -> None:
    u = _create_user(db_session, "exp@example.com", "pw")
    raw = "expiredtokentestvalueee"
    th = hash_refresh_token(raw)
    now = datetime.now(tz=UTC)
    db_session.add(
        PasswordResetToken(
            user_id=u.id,
            token_hash=th,
            expires_at=now - timedelta(hours=1),
            used_at=None,
            created_at=now - timedelta(hours=2),
        ),
    )
    db_session.commit()
    r = client.post(
        "/api/v1/auth/reset-password",
        json={"token": raw, "new_password": "nopepass123456"},
    )
    assert r.status_code == 400
