"""SPI BaseConnector — contrato interno dos plugins."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

from fourpro_contracts.connectors import (
    ConnectionTestResult,
    ConnectorCapability,
    ConnectorType,
    DiscoverResponse,
    SampleSchemaResponse,
)

ExtractFormat = Literal["csv", "json"]


@dataclass
class ExtractResult:
    """Metadados do ficheiro escrito em stage pelo plugin."""

    stage_path: Path
    format: ExtractFormat
    original_filename: str
    content_type: str
    size_bytes: int
    row_count: int | None = None
    object_id: str | None = None
    meta: dict[str, Any] = field(default_factory=dict)


class ConnectorError(Exception):
    """Erro de configuração ou execução do conector (mensagem segura)."""

    def __init__(self, message: str, *, technical: str | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.technical = technical or message


class BaseConnector(ABC):
    """Interface mínima de um plugin de fonte de dados."""

    connector_type: ConnectorType

    @abstractmethod
    def capabilities(self) -> ConnectorCapability:
        """Metadados expostos no catálogo GET /connectors."""

    @abstractmethod
    def validate_config(
        self,
        config: dict[str, Any],
        secret: dict[str, str] | None = None,
    ) -> None:
        """Valida config (sem segredos sensíveis em exceções)."""

    @abstractmethod
    def test_connection(
        self,
        config: dict[str, Any],
        secret: dict[str, str] | None = None,
    ) -> ConnectionTestResult:
        """Smoke de conectividade / credenciais."""

    @abstractmethod
    def discover(
        self,
        config: dict[str, Any],
        secret: dict[str, str] | None = None,
    ) -> DiscoverResponse:
        """Lista objectos (tabelas, paths, endpoints)."""

    @abstractmethod
    def sample_schema(
        self,
        config: dict[str, Any],
        secret: dict[str, str] | None = None,
        *,
        object_id: str,
        limit: int = 100,
    ) -> SampleSchemaResponse:
        """Infere colunas e devolve amostra de linhas."""

    @abstractmethod
    def extract(
        self,
        config: dict[str, Any],
        secret: dict[str, str] | None = None,
        *,
        stage_path: Path,
        object_id: str | None = None,
        mode: Literal["full", "sample"] = "full",
        sample_limit: int = 10_000,
    ) -> ExtractResult:
        """Extrai dados para `stage_path` (ficheiro CSV/JSON) e devolve metadados."""
