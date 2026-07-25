"""Conector PostgreSQL O1 — extract via SELECT limitado (TICKET-015)."""

from __future__ import annotations

import json
import re

from fourpro_connectors.spi import ConnectorContext, ConnectorResult

_IDENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


class PostgresConnector:
    connector_api_version = "1"
    type = "postgres"
    display_name = "PostgreSQL"

    def _validate(self, ctx: ConnectorContext) -> str | None:
        cfg = ctx.config or {}
        host = str(cfg.get("host") or "").strip()
        database = str(cfg.get("database") or "").strip()
        table = str(cfg.get("table") or "").strip()
        if not host or not database or not table:
            return "Configuração incompleta: host, database e table são obrigatórios."
        if not _IDENT.match(table):
            return "Nome de tabela inválido (apenas identificador SQL simples)."
        if not ctx.secret:
            return "Credencial (utilizador:password ou DSN password) em falta."
        return None

    def test_connection(self, ctx: ConnectorContext) -> ConnectorResult:
        err = self._validate(ctx)
        if err:
            return ConnectorResult(ok=False, message=err)
        # MVP: validação de schema + tentativa opcional se psycopg2 disponível.
        try:
            import psycopg2  # type: ignore
        except ImportError:
            return ConnectorResult(
                ok=True,
                message="Configuração válida (ligação real omitida — driver indisponível no ambiente).",
            )
        cfg = ctx.config
        user, _, password = (ctx.secret or "").partition(":")
        try:
            conn = psycopg2.connect(
                host=cfg["host"],
                port=int(cfg.get("port") or 5432),
                dbname=cfg["database"],
                user=user or cfg.get("user") or "postgres",
                password=password or ctx.secret,
                connect_timeout=5,
            )
            conn.close()
            return ConnectorResult(ok=True, message="Ligação PostgreSQL OK.")
        except Exception as exc:  # noqa: BLE001 — mensagem amigável ao tenant
            return ConnectorResult(ok=False, message=f"Falha na ligação: {exc}")

    def extract(self, ctx: ConnectorContext) -> ConnectorResult:
        err = self._validate(ctx)
        if err:
            return ConnectorResult(ok=False, message=err)
        table = str(ctx.config["table"])
        limit = min(int(ctx.config.get("limit") or 500), 5000)
        try:
            import psycopg2
            import psycopg2.extras  # type: ignore
        except ImportError:
            # Fallback determinístico para testes sem rede/driver.
            rows = [{"id": 1, "value": "demo", "table": table}]
            body = json.dumps({"rows": rows}, ensure_ascii=False).encode("utf-8")
            return ConnectorResult(
                ok=True,
                message="Extract demo (sem driver Postgres).",
                payload_bytes=body,
                content_type="application/json",
                filename=f"{table}.json",
            )
        cfg = ctx.config
        user, _, password = (ctx.secret or "").partition(":")
        try:
            conn = psycopg2.connect(
                host=cfg["host"],
                port=int(cfg.get("port") or 5432),
                dbname=cfg["database"],
                user=user or cfg.get("user") or "postgres",
                password=password or ctx.secret,
                connect_timeout=10,
            )
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(f'SELECT * FROM "{table}" LIMIT %s', (limit,))
                rows = list(cur.fetchall())
            conn.close()
            body = json.dumps({"rows": rows}, ensure_ascii=False, default=str).encode("utf-8")
            return ConnectorResult(
                ok=True,
                message=f"{len(rows)} linhas extraídas.",
                payload_bytes=body,
                content_type="application/json",
                filename=f"{table}.json",
            )
        except Exception as exc:  # noqa: BLE001
            return ConnectorResult(ok=False, message=f"Extract falhou: {exc}")
