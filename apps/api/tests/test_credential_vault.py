"""Unitários — cofre Fernet de credenciais."""

import pytest
from cryptography.fernet import Fernet

from fourpro_api.config import reset_settings_cache
from fourpro_api.services.credential_vault import decrypt_secret, encrypt_secret


@pytest.mark.unit
@pytest.mark.security
def test_encrypt_decrypt_round_trip_from_jwt_secret() -> None:
    reset_settings_cache()
    blob = encrypt_secret("super-secret")
    assert decrypt_secret(blob) == "super-secret"


@pytest.mark.unit
@pytest.mark.security
def test_decrypt_invalid_token_raises(monkeypatch) -> None:
    monkeypatch.setenv("CREDENTIALS_FERNET_KEY", Fernet.generate_key().decode("utf-8"))
    reset_settings_cache()
    with pytest.raises(ValueError, match="desencriptar"):
        decrypt_secret(b"not-a-valid-fernet-token")
    monkeypatch.delenv("CREDENTIALS_FERNET_KEY", raising=False)
    reset_settings_cache()
