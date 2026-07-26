"""Interface de plugin de conector (SPI)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass
class ConnectorContext:
    tenant_id: str
    data_source_id: str
    config: dict[str, Any]
    secret: str | None = None
    correlation_id: str | None = None


@dataclass
class ConnectorResult:
    ok: bool
    message: str
    payload_bytes: bytes | None = None
    content_type: str | None = None
    filename: str | None = None
    meta: dict[str, Any] = field(default_factory=dict)


class DataConnector(Protocol):
    connector_api_version: str
    type: str
    display_name: str

    def test_connection(self, ctx: ConnectorContext) -> ConnectorResult: ...

    def extract(self, ctx: ConnectorContext) -> ConnectorResult: ...
