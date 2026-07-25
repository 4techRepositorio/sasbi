"""Conector REST JSON — allowlist de hosts e bloqueio de IPs privados."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Literal
from urllib.parse import urljoin

import httpx
from fourpro_contracts.connectors import (
    ConnectionTestResult,
    ConnectorCapability,
    DiscoverObject,
    DiscoverResponse,
    SampleSchemaResponse,
    SchemaColumn,
)

from fourpro_connectors.base import BaseConnector, ConnectorError, ExtractResult
from fourpro_connectors.plugins._io import infer_type, write_rows_json
from fourpro_connectors.registry import register
from fourpro_connectors.security import validate_http_url


def _base_url(config: dict[str, Any]) -> str:
    base = config.get("base_url") or config.get("url")
    if not base:
        raise ConnectorError("Config rest_json exige base_url")
    return str(base).rstrip("/") + "/"


def _allow_private(config: dict[str, Any]) -> bool:
    return bool(config.get("allow_private_hosts") is True)


def _allowed_hosts(config: dict[str, Any]) -> list[str] | None:
    raw = config.get("allowed_hosts")
    if raw is None:
        return None
    if not isinstance(raw, list):
        raise ConnectorError("allowed_hosts deve ser lista de hosts")
    return [str(h) for h in raw]


def _auth_headers(secret: dict[str, str] | None, config: dict[str, Any]) -> dict[str, str]:
    headers: dict[str, str] = {}
    extra = config.get("headers")
    if isinstance(extra, dict):
        for k, v in extra.items():
            if str(k).lower() in ("authorization", "x-api-key"):
                continue  # segredos só via secret
            headers[str(k)] = str(v)
    secret = secret or {}
    if secret.get("token"):
        headers["Authorization"] = f"Bearer {secret['token']}"
    elif secret.get("api_key"):
        header_name = str(config.get("api_key_header") or "X-API-Key")
        headers[header_name] = secret["api_key"]
    elif secret.get("username") and secret.get("password"):
        # Basic via httpx auth preferred; header built at request time
        pass
    return headers


def _resolve_url(config: dict[str, Any], object_id: str | None) -> str:
    base = _base_url(config)
    path = object_id or config.get("default_object") or config.get("path") or ""
    url = urljoin(base, str(path).lstrip("/"))
    validate_http_url(
        url,
        allow_private=_allow_private(config),
        allowed_hosts=_allowed_hosts(config),
    )
    return url


def _dig(data: Any, path: str | None) -> Any:
    if not path:
        return data
    cur = data
    for part in path.split("."):
        if isinstance(cur, dict):
            cur = cur.get(part)
        else:
            return None
    return cur


def _as_rows(payload: Any, items_path: str | None) -> list[dict[str, Any]]:
    data = _dig(payload, items_path) if items_path else payload
    if isinstance(data, dict):
        return [data]
    if isinstance(data, list):
        return [r for r in data if isinstance(r, dict)]
    raise ConnectorError("Resposta REST não é objecto/array JSON utilizável")


def _request(
    config: dict[str, Any],
    secret: dict[str, str] | None,
    url: str,
) -> Any:
    method = str(config.get("method") or "GET").upper()
    if method not in ("GET", "POST"):
        raise ConnectorError("method deve ser GET ou POST")
    headers = _auth_headers(secret, config)
    auth = None
    secret = secret or {}
    if secret.get("username") and secret.get("password") and "Authorization" not in headers:
        auth = (secret["username"], secret["password"])
    timeout = float(config.get("timeout_seconds") or 30)
    with httpx.Client(timeout=timeout, follow_redirects=False) as client:
        if method == "GET":
            resp = client.get(url, headers=headers, auth=auth)
        else:
            body = config.get("body")
            resp = client.post(url, headers=headers, auth=auth, json=body)
    if resp.status_code >= 400:
        raise ConnectorError(f"HTTP {resp.status_code} na fonte REST")
    try:
        return resp.json()
    except json.JSONDecodeError as e:
        raise ConnectorError("Resposta não é JSON válido") from e


@register
class RestJsonConnector(BaseConnector):
    connector_type = "rest_json"

    def capabilities(self) -> ConnectorCapability:
        return ConnectorCapability(
            connector_type="rest_json",
            display_name="REST JSON",
            description="API HTTP JSON com allowlist de hosts (SSRF mitigation)",
            auth_kinds=["none", "token", "api_key", "password"],
            supports_incremental=False,
            supports_discover=True,
            max_sample_rows=100,
            config_schema_hint={
                "base_url": "https://api.example.com",
                "path": "/v1/items",
                "allowed_hosts": ["api.example.com"],
                "allow_private_hosts": False,
                "items_path": "data.items",
                "method": "GET",
            },
        )

    def validate_config(
        self,
        config: dict[str, Any],
        secret: dict[str, str] | None = None,
    ) -> None:
        _ = secret
        base = _base_url(config)
        validate_http_url(
            base.rstrip("/"),
            allow_private=_allow_private(config),
            allowed_hosts=_allowed_hosts(config),
        )

    def test_connection(
        self,
        config: dict[str, Any],
        secret: dict[str, str] | None = None,
    ) -> ConnectionTestResult:
        try:
            url = _resolve_url(config, None)
            payload = _request(config, secret, url)
            rows = _as_rows(payload, config.get("items_path"))
            return ConnectionTestResult(
                ok=True,
                message="Endpoint REST acessível",
                details={"sample_row_count": min(len(rows), 5)},
            )
        except ConnectorError as e:
            return ConnectionTestResult(ok=False, message=e.message)
        except ValueError as e:
            return ConnectionTestResult(ok=False, message=str(e))
        except httpx.HTTPError:
            return ConnectionTestResult(ok=False, message="Erro de rede HTTP")

    def discover(
        self,
        config: dict[str, Any],
        secret: dict[str, str] | None = None,
    ) -> DiscoverResponse:
        _ = secret
        path = config.get("path") or config.get("default_object") or "/"
        objects = [
            DiscoverObject(
                object_id=str(path).lstrip("/"),
                name=str(path),
                kind="endpoint",
                meta={"method": config.get("method") or "GET"},
            )
        ]
        extra = config.get("endpoints")
        if isinstance(extra, list):
            for ep in extra:
                objects.append(
                    DiscoverObject(object_id=str(ep), name=str(ep), kind="endpoint", meta={})
                )
        return DiscoverResponse(objects=objects)

    def sample_schema(
        self,
        config: dict[str, Any],
        secret: dict[str, str] | None = None,
        *,
        object_id: str,
        limit: int = 100,
    ) -> SampleSchemaResponse:
        url = _resolve_url(config, object_id)
        payload = _request(config, secret, url)
        rows = _as_rows(payload, config.get("items_path"))[:limit]
        cols = list(rows[0].keys()) if rows else []
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
        url = _resolve_url(config, object_id)
        all_rows: list[dict[str, Any]] = []
        page_param = config.get("page_param")
        page_size_param = config.get("page_size_param")
        max_pages = int(config.get("max_pages") or 1)
        if mode == "sample":
            max_pages = 1

        if page_param:
            for page in range(1, max_pages + 1):
                sep = "&" if "?" in url else "?"
                page_url = f"{url}{sep}{page_param}={page}"
                if page_size_param:
                    page_url += f"&{page_size_param}={min(sample_limit, 1000)}"
                payload = _request(config, secret, page_url)
                batch = _as_rows(payload, config.get("items_path"))
                if not batch:
                    break
                all_rows.extend(batch)
                if mode == "sample" and len(all_rows) >= sample_limit:
                    all_rows = all_rows[:sample_limit]
                    break
        else:
            payload = _request(config, secret, url)
            all_rows = _as_rows(payload, config.get("items_path"))
            if mode == "sample":
                all_rows = all_rows[:sample_limit]

        stage_path = Path(stage_path)
        write_rows_json(stage_path, all_rows)
        size = stage_path.stat().st_size
        return ExtractResult(
            stage_path=stage_path.resolve(),
            format="json",
            original_filename=stage_path.name,
            content_type="application/json",
            size_bytes=size,
            row_count=len(all_rows),
            object_id=object_id or str(config.get("path") or ""),
            meta={"url_host": httpx.URL(url).host},
        )
