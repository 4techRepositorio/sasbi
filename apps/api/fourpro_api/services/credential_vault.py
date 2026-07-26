"""Cofre de credenciais Fernet para conectores (TICKET-015)."""

from __future__ import annotations

import base64
import hashlib

from cryptography.fernet import Fernet, InvalidToken

from fourpro_api.config import get_settings


def _fernet() -> Fernet:
    settings = get_settings()
    raw = settings.credentials_fernet_key
    if raw:
        key = raw.encode("utf-8") if isinstance(raw, str) else raw
    else:
        digest = hashlib.sha256(settings.jwt_secret.encode("utf-8")).digest()
        key = base64.urlsafe_b64encode(digest)
    return Fernet(key)


def encrypt_secret(plain: str) -> bytes:
    return _fernet().encrypt(plain.encode("utf-8"))


def decrypt_secret(blob: bytes) -> str:
    try:
        return _fernet().decrypt(blob).decode("utf-8")
    except InvalidToken as exc:
        raise ValueError("Não foi possível desencriptar a credencial") from exc
