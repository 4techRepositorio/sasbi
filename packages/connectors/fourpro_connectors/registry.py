"""Registry de conectores."""

from __future__ import annotations

from fourpro_connectors.plugins.file import FileConnector
from fourpro_connectors.plugins.postgres import PostgresConnector
from fourpro_connectors.plugins.rest_json import RestJsonConnector
from fourpro_connectors.spi import DataConnector

_REGISTRY: dict[str, DataConnector] = {
    "file": FileConnector(),
    "postgres": PostgresConnector(),
    "rest_json": RestJsonConnector(),
}


def get_connector(connector_type: str) -> DataConnector | None:
    return _REGISTRY.get(connector_type)


def list_connector_types() -> list[DataConnector]:
    return list(_REGISTRY.values())
