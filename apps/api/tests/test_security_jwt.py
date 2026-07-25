"""Unitários — JWT access / MFA pending."""

import uuid
from datetime import UTC, datetime, timedelta

import pytest
from jose import jwt

from fourpro_api.config import get_settings, reset_settings_cache
from fourpro_api.core.security import (
    create_access_token,
    create_mfa_pending_token,
    decode_access_token,
    decode_mfa_pending_token,
    hash_otp_code,
    hash_refresh_token,
    new_refresh_token_value,
)


@pytest.mark.unit
@pytest.mark.security
@pytest.mark.auth
def test_access_token_round_trip() -> None:
    uid, tid = uuid.uuid4(), uuid.uuid4()
    token, expires = create_access_token(uid, tid, "admin")
    assert expires > 0
    principal = decode_access_token(token)
    assert principal is not None
    assert principal.user_id == uid
    assert principal.tenant_id == tid
    assert principal.role == "admin"


@pytest.mark.unit
@pytest.mark.security
def test_decode_access_rejects_wrong_typ_and_garbage() -> None:
    settings = get_settings()
    bad_typ = jwt.encode(
        {
            "sub": str(uuid.uuid4()),
            "tid": str(uuid.uuid4()),
            "role": "admin",
            "exp": datetime.now(tz=UTC) + timedelta(minutes=5),
            "typ": "refresh",
        },
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )
    assert decode_access_token(bad_typ) is None
    assert decode_access_token("not-a-jwt") is None
    incomplete = jwt.encode(
        {
            "sub": str(uuid.uuid4()),
            "exp": datetime.now(tz=UTC) + timedelta(minutes=5),
            "typ": "access",
        },
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )
    assert decode_access_token(incomplete) is None


@pytest.mark.unit
@pytest.mark.security
@pytest.mark.auth
def test_mfa_pending_token_round_trip_and_rejects_access_typ() -> None:
    uid = uuid.uuid4()
    token = create_mfa_pending_token(uid)
    assert decode_mfa_pending_token(token) == uid
    access, _ = create_access_token(uid, uuid.uuid4(), "admin")
    assert decode_mfa_pending_token(access) is None
    assert decode_mfa_pending_token("broken") is None
    settings = get_settings()
    no_sub = jwt.encode(
        {
            "exp": datetime.now(tz=UTC) + timedelta(minutes=5),
            "typ": "mfa_pending",
        },
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )
    assert decode_mfa_pending_token(no_sub) is None


@pytest.mark.unit
@pytest.mark.security
def test_token_helpers_deterministic_hashes() -> None:
    reset_settings_cache()
    raw = new_refresh_token_value()
    assert len(raw) > 20
    assert hash_refresh_token(raw) == hash_refresh_token(raw)
    assert hash_otp_code("123456") != hash_otp_code("000000")
