"""Chave de rate limit com / sem confiança em X-Forwarded-For."""

from unittest.mock import MagicMock

import pytest

from fourpro_api.config import reset_settings_cache
from fourpro_api.rate_limit_key import client_key_for_rate_limit


@pytest.fixture(autouse=True)
def _reset_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("RATE_LIMIT_TRUST_PROXY", raising=False)
    reset_settings_cache()
    yield
    reset_settings_cache()


def test_without_trust_proxy_uses_socket_peer(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("RATE_LIMIT_TRUST_PROXY", "false")
    reset_settings_cache()
    req = MagicMock()
    req.headers.get.return_value = "203.0.113.5, 10.0.0.1"
    req.client.host = "192.168.1.1"
    assert client_key_for_rate_limit(req) == "192.168.1.1"


def test_with_trust_proxy_uses_leftmost_xff(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("RATE_LIMIT_TRUST_PROXY", "true")
    reset_settings_cache()
    req = MagicMock()
    req.headers.get.side_effect = lambda name, default=None: (
        "203.0.113.5, 10.0.0.1" if name.lower() == "x-forwarded-for" else default
    )
    req.client.host = "10.0.0.2"
    assert client_key_for_rate_limit(req) == "203.0.113.5"


def test_trust_proxy_falls_back_when_header_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("RATE_LIMIT_TRUST_PROXY", "true")
    reset_settings_cache()
    req = MagicMock()
    req.headers.get.return_value = None
    req.client.host = "10.0.0.2"
    assert client_key_for_rate_limit(req) == "10.0.0.2"
