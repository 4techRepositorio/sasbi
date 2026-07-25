"""Helpers de segurança para plugins (URL, SQL, redaction)."""

from __future__ import annotations

import ipaddress
import logging
import re
import socket
from urllib.parse import urlparse

_SECRET_KEYS = frozenset(
    {
        "password",
        "token",
        "api_key",
        "apikey",
        "secret",
        "secret_key",
        "access_key",
        "access_key_id",
        "authorization",
        "private_key",
        "client_secret",
    }
)

_IDENT_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def redact_mapping(data: dict[str, object] | None) -> dict[str, object]:
    """Cópia com valores de chaves sensíveis mascarados (para logs)."""
    if not data:
        return {}
    out: dict[str, object] = {}
    for k, v in data.items():
        if k.lower() in _SECRET_KEYS or "password" in k.lower() or "secret" in k.lower():
            out[k] = "***"
        elif isinstance(v, dict):
            out[k] = redact_mapping(v)  # type: ignore[arg-type]
        else:
            out[k] = v
    return out


class RedactingFilter(logging.Filter):
    """Evita que passwords/tokens apareçam em mensagens de log."""

    _PATTERNS = [
        re.compile(r"(password|token|api[_-]?key|secret)([\"']?\s*[:=]\s*[\"']?)([^\"'\s,}&]+)", re.I),
    ]

    def filter(self, record: logging.LogRecord) -> bool:
        msg = record.getMessage()
        for pat in self._PATTERNS:
            msg = pat.sub(r"\1\2***", msg)
        record.msg = msg
        record.args = ()
        return True


def assert_safe_sql_identifier(name: str, *, label: str = "identifier") -> str:
    """Aceita apenas identificadores SQL simples (sem raw SQL do cliente)."""
    if not name or not _IDENT_RE.match(name):
        raise ValueError(f"{label} inválido: use apenas [A-Za-z_][A-Za-z0-9_]*")
    return name


def split_object_id(object_id: str) -> tuple[str | None, str]:
    """`schema.table` ou `table` → (schema|None, table)."""
    parts = object_id.split(".")
    if len(parts) == 1:
        return None, assert_safe_sql_identifier(parts[0], label="table")
    if len(parts) == 2:
        return (
            assert_safe_sql_identifier(parts[0], label="schema"),
            assert_safe_sql_identifier(parts[1], label="table"),
        )
    raise ValueError("object_id inválido; use table ou schema.table")


def quote_ident(name: str) -> str:
    assert_safe_sql_identifier(name)
    return '"' + name.replace('"', "") + '"'


def is_private_or_local_ip(ip: ipaddress.IPv4Address | ipaddress.IPv6Address) -> bool:
    return bool(
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_reserved
        or ip.is_multicast
        or (isinstance(ip, ipaddress.IPv4Address) and ip == ipaddress.IPv4Address("169.254.169.254"))
    )


def validate_http_url(
    url: str,
    *,
    allow_private: bool = False,
    allowed_hosts: list[str] | None = None,
) -> str:
    """Valida URL HTTP(S); bloqueia SSRF para IPs privados salvo allow_private."""
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise ValueError("URL deve usar http ou https")
    host = parsed.hostname
    if not host:
        raise ValueError("URL sem host")
    if allowed_hosts:
        allowed_lower = {h.lower() for h in allowed_hosts}
        if host.lower() not in allowed_lower:
            raise ValueError(f"Host '{host}' não está na allowlist")

    if allow_private:
        return url

    try:
        infos = socket.getaddrinfo(host, parsed.port or 443, type=socket.SOCK_STREAM)
    except socket.gaierror as e:
        raise ValueError(f"Não foi possível resolver o host: {host}") from e

    for info in infos:
        sockaddr = info[4]
        ip_str = sockaddr[0]
        try:
            ip = ipaddress.ip_address(ip_str)
        except ValueError:
            continue
        if is_private_or_local_ip(ip):
            raise ValueError(
                "URL aponta para endereço privado/local; "
                "defina allow_private_hosts=true na config apenas se necessário"
            )
    return url
