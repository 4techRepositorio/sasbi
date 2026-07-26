"""SPI de conectores 4Pro_BI (TICKET-015)."""

from fourpro_connectors.registry import get_connector, list_connector_types
from fourpro_connectors.spi import ConnectorContext, ConnectorResult, DataConnector

__all__ = [
    "ConnectorContext",
    "ConnectorResult",
    "DataConnector",
    "get_connector",
    "list_connector_types",
]
