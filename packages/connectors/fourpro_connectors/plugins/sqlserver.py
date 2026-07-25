"""Conector SQL Server — identificadores validados; sem SQL livre do cliente."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

from fourpro_contracts.connectors import (
    ConnectionTestResult,
    ConnectorCapability,
    DiscoverObject,
    DiscoverResponse,
    SampleSchemaResponse,
    SchemaColumn,
)

from fourpro_connectors.base import BaseConnector, ConnectorError, ExtractResult
from fourpro_connectors.plugins._io import infer_type, write_rows_csv
from fourpro_connectors.plugins._sql_common import (
    fetch_rows,
    require_host_port_db,
    resolve_table,
)
from fourpro_connectors.registry import register


def _connect(config: dict[str, Any], secret: dict[str, str] | None):
    try:
        import pyodbc
    except ImportError as e:
        raise ConnectorError(
            "Driver SQL Server não instalado (pyodbc)",
            technical="pip install pyodbc",
        ) from e
    host, port, database = require_host_port_db(config)
    port = port or 1433
    secret = secret or {}
    user = secret.get("username") or secret.get("user") or config.get("username")
    password = secret.get("password") or ""
    if not user:
        raise ConnectorError("Credencial username obrigatória")
    driver = config.get("odbc_driver") or "ODBC Driver 18 for SQL Server"
    conn_str = (
        f"DRIVER={{{driver}}};SERVER={host},{port};DATABASE={database};"
        f"UID={user};PWD={password};TrustServerCertificate=yes;"
    )
    return pyodbc.connect(conn_str, timeout=int(config.get("connect_timeout", 10)))


@register
class SqlServerConnector(BaseConnector):
    connector_type = "sqlserver"

    def capabilities(self) -> ConnectorCapability:
        return ConnectorCapability(
            connector_type="sqlserver",
            display_name="SQL Server",
            description="Tabelas SQL Server (SELECT TOP; sem SQL livre do cliente)",
            auth_kinds=["password"],
            supports_incremental=False,
            supports_discover=True,
            max_sample_rows=100,
            config_schema_hint={
                "host": "string",
                "port": 1433,
                "database": "string",
                "schema": "dbo",
                "odbc_driver": "ODBC Driver 18 for SQL Server",
            },
        )

    def validate_config(
        self,
        config: dict[str, Any],
        secret: dict[str, str] | None = None,
    ) -> None:
        require_host_port_db(config)
        _ = secret

    def test_connection(
        self,
        config: dict[str, Any],
        secret: dict[str, str] | None = None,
    ) -> ConnectionTestResult:
        try:
            conn = _connect(config, secret)
            try:
                cur = conn.cursor()
                cur.execute("SELECT 1")
                cur.fetchone()
                cur.close()
            finally:
                conn.close()
            return ConnectionTestResult(ok=True, message="Ligação SQL Server OK")
        except ConnectorError as e:
            return ConnectionTestResult(ok=False, message=e.message)
        except Exception as e:  # noqa: BLE001
            return ConnectionTestResult(
                ok=False, message="Falha na ligação SQL Server", details={"error": type(e).__name__}
            )

    def discover(
        self,
        config: dict[str, Any],
        secret: dict[str, str] | None = None,
    ) -> DiscoverResponse:
        schema = config.get("schema") or "dbo"
        conn = _connect(config, secret)
        try:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT TABLE_SCHEMA, TABLE_NAME
                FROM INFORMATION_SCHEMA.TABLES
                WHERE TABLE_TYPE = 'BASE TABLE' AND TABLE_SCHEMA = ?
                ORDER BY TABLE_NAME
                """,
                (schema,),
            )
            rows = cur.fetchall()
            cur.close()
        finally:
            conn.close()
        objects = [
            DiscoverObject(object_id=f"{s}.{t}", name=t, kind="table", meta={"schema": s})
            for s, t in rows
        ]
        return DiscoverResponse(objects=objects)

    def sample_schema(
        self,
        config: dict[str, Any],
        secret: dict[str, str] | None = None,
        *,
        object_id: str,
        limit: int = 100,
    ) -> SampleSchemaResponse:
        schema, table = resolve_table(config, object_id)
        conn = _connect(config, secret)
        try:
            cur = conn.cursor()
            cols, rows = fetch_rows(
                cur, schema=schema or "dbo", table=table, dialect="sqlserver", limit=limit
            )
            cur.close()
        finally:
            conn.close()
        columns = [
            SchemaColumn(
                name=c,
                inferred_type=infer_type(rows[0].get(c)) if rows else "string",
            )
            for c in cols
        ]
        return SampleSchemaResponse(object_id=object_id, columns=columns, sample_rows=rows)

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
        schema, table = resolve_table(config, object_id)
        limit = sample_limit if mode == "sample" else int(config.get("max_rows") or sample_limit)
        conn = _connect(config, secret)
        try:
            cur = conn.cursor()
            cols, rows = fetch_rows(
                cur, schema=schema or "dbo", table=table, dialect="sqlserver", limit=limit
            )
            cur.close()
        finally:
            conn.close()
        stage_path = Path(stage_path)
        write_rows_csv(stage_path, rows, cols)
        size = stage_path.stat().st_size
        oid = f"{schema}.{table}" if schema else table
        return ExtractResult(
            stage_path=stage_path.resolve(),
            format="csv",
            original_filename=stage_path.name,
            content_type="text/csv",
            size_bytes=size,
            row_count=len(rows),
            object_id=oid,
            meta={"dialect": "sqlserver"},
        )
