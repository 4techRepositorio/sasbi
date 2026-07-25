"""Registry de tipos de conector."""

from __future__ import annotations

from typing import TYPE_CHECKING

from fourpro_contracts.connectors import ConnectorCapability, ConnectorType

if TYPE_CHECKING:
    from fourpro_connectors.base import BaseConnector

_REGISTRY: dict[ConnectorType, type[BaseConnector]] = {}
_BUILTIN_REGISTERED = False


def register(connector_cls: type[BaseConnector]) -> type[BaseConnector]:
    ctype = connector_cls.connector_type  # type: ignore[attr-defined]
    _REGISTRY[ctype] = connector_cls
    return connector_cls


def get_connector(connector_type: ConnectorType | str) -> BaseConnector:
    if connector_type not in _REGISTRY:
        raise KeyError(f"Conector desconhecido: {connector_type}")
    return _REGISTRY[connector_type]()  # type: ignore[index]


def list_connector_types() -> list[ConnectorType]:
    return list(_REGISTRY.keys())  # type: ignore[return-value]


def list_capabilities() -> list[ConnectorCapability]:
    return [cls().capabilities() for cls in _REGISTRY.values()]


def register_builtin_connectors() -> None:
    global _BUILTIN_REGISTERED
    if _BUILTIN_REGISTERED:
        return
    from fourpro_connectors.plugins import (  # noqa: F401
        file as _file,
        mysql as _mysql,
        postgres as _postgres,
        rest_json as _rest,
        s3_compatible as _s3,
        sqlserver as _sqlserver,
    )

    _BUILTIN_REGISTERED = True
