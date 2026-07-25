"""SPI e plugins de conectores 4Pro_BI."""

from fourpro_connectors.base import BaseConnector, ExtractResult
from fourpro_connectors.registry import (
    get_connector,
    list_capabilities,
    list_connector_types,
    register_builtin_connectors,
)

register_builtin_connectors()

__all__ = [
    "BaseConnector",
    "ExtractResult",
    "get_connector",
    "list_capabilities",
    "list_connector_types",
    "register_builtin_connectors",
]
