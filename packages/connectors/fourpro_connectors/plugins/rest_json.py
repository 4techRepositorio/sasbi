"""Conector REST JSON O1 com allowlist de hosts (TICKET-015)."""

from __future__ import annotations

import ipaddress
import json
import socket
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from fourpro_connectors.spi import ConnectorContext, ConnectorResult


def _host_allowed(url: str, allowlist: list[str]) -> bool:
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()
    if not host:
        return False
    if allowlist:
        return host in {h.lower() for h in allowlist}
    # Sem allowlist: bloquear IPs privados / loopback por defeito.
    try:
        infos = socket.getaddrinfo(host, None)
        for info in infos:
            ip = ipaddress.ip_address(info[4][0])
            if ip.is_private or ip.is_loopback or ip.is_link_local:
                return False
    except OSError:
        return False
    return parsed.scheme in ("http", "https")


class RestJsonConnector:
    connector_api_version = "1"
    type = "rest_json"
    display_name = "REST JSON"

    def test_connection(self, ctx: ConnectorContext) -> ConnectorResult:
        url = str((ctx.config or {}).get("url") or "").strip()
        allow = list((ctx.config or {}).get("allowlist_hosts") or [])
        if not url:
            return ConnectorResult(ok=False, message="URL obrigatória.")
        if not _host_allowed(url, allow):
            return ConnectorResult(ok=False, message="Host não permitido (allowlist / rede privada).")
        return ConnectorResult(ok=True, message="URL válida segundo a política de egress.")

    def extract(self, ctx: ConnectorContext) -> ConnectorResult:
        url = str((ctx.config or {}).get("url") or "").strip()
        allow = list((ctx.config or {}).get("allowlist_hosts") or [])
        if not url:
            return ConnectorResult(ok=False, message="URL obrigatória.")
        if not _host_allowed(url, allow):
            return ConnectorResult(ok=False, message="Host não permitido (allowlist / rede privada).")
        headers = {"Accept": "application/json", "User-Agent": "4Pro_BI-connector/1"}
        if ctx.secret:
            headers["Authorization"] = f"Bearer {ctx.secret}"
        try:
            req = Request(url, headers=headers, method="GET")
            with urlopen(req, timeout=15) as resp:  # noqa: S310 — host validado acima
                raw = resp.read()
            # Validar JSON
            json.loads(raw.decode("utf-8"))
            return ConnectorResult(
                ok=True,
                message="JSON obtido.",
                payload_bytes=raw,
                content_type="application/json",
                filename="rest.json",
            )
        except Exception as exc:  # noqa: BLE001
            # Fallback determinístico para testes offline com allowlist local fictícia.
            if (ctx.config or {}).get("demo_fallback"):
                body = json.dumps({"items": [{"id": 1, "name": "demo"}]}).encode("utf-8")
                return ConnectorResult(
                    ok=True,
                    message="Extract demo (fallback).",
                    payload_bytes=body,
                    content_type="application/json",
                    filename="rest-demo.json",
                )
            return ConnectorResult(ok=False, message=f"Pedido REST falhou: {exc}")
