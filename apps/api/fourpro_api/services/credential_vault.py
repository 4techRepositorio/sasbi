"""Cofre de credenciais (Fernet) — Core / TICKET-015."""

from __future__ import annotations

import base64
import hashlib
import json
import logging
from typing import Any

from cryptography.fernet import Fernet, InvalidToken

from fourpro_api.config import Settings, get_settings

logger = logging.getLogger(__name__)

KEY_VERSION_CURRENT = 1


def _derive_fernet_key_from_jwt(jwt_secret: str) -> bytes:
    digest = hashlib.sha256(f"fourpro-credentials-v1:{jwt_secret}".encode()).digest()
    return base64.urlsafe_b64encode(digest)


def resolve_fernet(settings: Settings | None = None) -> tuple[Fernet, int]:
    """Devolve Fernet + key_version.

    Produção: exige CREDENTIALS_FERNET_KEY.
    Dev: se ausente, deriva de JWT_SECRET (com warning documentado).
    """
    settings = settings or get_settings()
    raw = (settings.credentials_fernet_key or "").strip()
    if raw:
        key = raw.encode("utf-8") if isinstance(raw, str) else raw
        return Fernet(key), KEY_VERSION_CURRENT

    if settings.environment.lower() in ("production", "prod"):
        raise RuntimeError(
            "CREDENTIALS_FERNET_KEY é obrigatório em produção "
            "(gerar com cryptography.fernet.Fernet.generate_key())"
        )

    logger.warning(
        "CREDENTIALS_FERNET_KEY ausente: a derivar chave do JWT_SECRET (apenas desenvolvimento). "
        "Não use esta derivação em produção."
    )
    return Fernet(_derive_fernet_key_from_jwt(settings.jwt_secret)), KEY_VERSION_CURRENT


class CredentialVault:
    def __init__(self, settings: Settings | None = None) -> None:
        self._fernet, self.key_version = resolve_fernet(settings)

    def encrypt_dict(self, secret: dict[str, str]) -> str:
        payload = json.dumps(secret, separators=(",", ":"), sort_keys=True).encode("utf-8")
        return self._fernet.encrypt(payload).decode("utf-8")

    def decrypt_dict(self, token: str) -> dict[str, str]:
        try:
            raw = self._fernet.decrypt(token.encode("utf-8"))
        except InvalidToken as e:
            raise ValueError("Falha ao desencriptar credencial") from e
        data = json.loads(raw.decode("utf-8"))
        if not isinstance(data, dict):
            raise ValueError("Payload de credencial inválido")
        return {str(k): str(v) for k, v in data.items()}

    def encrypt_any(self, secret: dict[str, Any]) -> str:
        return self.encrypt_dict({str(k): str(v) for k, v in secret.items()})
