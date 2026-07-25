"""Helpers SQL partilhados (postgres / mysql / sqlserver) — sem raw SQL do cliente."""

from __future__ import annotations

from typing import Any, Protocol

from fourpro_connectors.base import ConnectorError
from fourpro_connectors.security import assert_safe_sql_identifier, quote_ident, split_object_id


class _Cursor(Protocol):
    description: Any

    def execute(self, query: str, params: Any = ()) -> Any: ...

    def fetchall(self) -> list[Any]: ...

    def fetchmany(self, size: int) -> list[Any]: ...

    def close(self) -> None: ...


def require_host_port_db(config: dict[str, Any]) -> tuple[str, int, str]:
    host = config.get("host")
    database = config.get("database")
    if not host or not database:
        raise ConnectorError("Config SQL exige host e database")
    port = int(config.get("port") or 0)
    return str(host), port, str(database)


def resolve_table(
    config: dict[str, Any],
    object_id: str | None,
) -> tuple[str | None, str]:
    oid = object_id or config.get("default_object") or config.get("table")
    if not oid:
        raise ConnectorError("object_id ou config.table é obrigatório")
    schema_cfg = config.get("schema")
    if "." not in str(oid) and schema_cfg:
        assert_safe_sql_identifier(str(schema_cfg), label="schema")
        return str(schema_cfg), assert_safe_sql_identifier(str(oid), label="table")
    return split_object_id(str(oid))


def qualified_name(schema: str | None, table: str, *, dialect: str) -> str:
    if dialect == "mysql":
        # MySQL usa backticks; schema ≈ database
        def qb(n: str) -> str:
            assert_safe_sql_identifier(n)
            return f"`{n}`"

        return f"{qb(schema)}.{qb(table)}" if schema else qb(table)
    if dialect == "sqlserver":
        def qb(n: str) -> str:
            assert_safe_sql_identifier(n)
            return f"[{n}]"

        return f"{qb(schema)}.{qb(table)}" if schema else qb(table)
    # postgres
    return f"{quote_ident(schema)}.{quote_ident(table)}" if schema else quote_ident(table)


def fetch_rows(
    cursor: _Cursor,
    *,
    schema: str | None,
    table: str,
    dialect: str,
    limit: int | None,
) -> tuple[list[str], list[dict[str, Any]]]:
    qname = qualified_name(schema, table, dialect=dialect)
    # LIMIT/TOP com inteiro validado — nunca SQL livre do cliente
    if limit is not None:
        if not isinstance(limit, int) or limit < 1 or limit > 1_000_000:
            raise ConnectorError("limit inválido")
        if dialect == "sqlserver":
            sql = f"SELECT TOP ({limit}) * FROM {qname}"
        else:
            sql = f"SELECT * FROM {qname} LIMIT {limit}"
    else:
        sql = f"SELECT * FROM {qname}"
    cursor.execute(sql)
    cols = [d[0] for d in (cursor.description or [])]
    raw = cursor.fetchall()
    rows: list[dict[str, Any]] = []
    for tup in raw:
        rows.append({cols[i]: tup[i] for i in range(len(cols))})
    return cols, rows
