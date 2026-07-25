"""Conector file — compatível com upload local (TICKET-015)."""

from __future__ import annotations

import json
from pathlib import Path

from fourpro_connectors.spi import ConnectorContext, ConnectorResult


class FileConnector:
    connector_api_version = "1"
    type = "file"
    display_name = "Ficheiro"

    def test_connection(self, ctx: ConnectorContext) -> ConnectorResult:
        path = (ctx.config or {}).get("path")
        if not path:
            return ConnectorResult(ok=True, message="Pronto para receber upload de ficheiro.")
        p = Path(str(path))
        if p.is_file():
            return ConnectorResult(ok=True, message="Ficheiro acessível.")
        return ConnectorResult(ok=False, message="Caminho de ficheiro inválido ou inacessível.")

    def extract(self, ctx: ConnectorContext) -> ConnectorResult:
        path = (ctx.config or {}).get("path")
        if path and Path(str(path)).is_file():
            data = Path(str(path)).read_bytes()
            name = Path(str(path)).name
            return ConnectorResult(
                ok=True,
                message="Ficheiro lido.",
                payload_bytes=data,
                content_type="application/octet-stream",
                filename=name,
            )
        # Sync sem path: produz manifesto JSON (útil para smoke / Desktop).
        body = json.dumps(
            {"source": "file", "tenant_id": ctx.tenant_id, "note": "empty_file_connector"},
            ensure_ascii=False,
        ).encode("utf-8")
        return ConnectorResult(
            ok=True,
            message="Manifesto file gerado.",
            payload_bytes=body,
            content_type="application/json",
            filename="file-source.json",
        )
