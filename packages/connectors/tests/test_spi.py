"""Testes unitários do SPI / segurança / file + rest (mock)."""

from __future__ import annotations

import json
from pathlib import Path

import httpx
import pytest

from fourpro_connectors import get_connector, list_capabilities, list_connector_types
from fourpro_connectors.security import assert_safe_sql_identifier, validate_http_url


def test_registry_has_all_types() -> None:
    types = set(list_connector_types())
    assert types == {
        "file",
        "postgres",
        "mysql",
        "sqlserver",
        "rest_json",
        "s3_compatible",
    }
    caps = list_capabilities()
    assert len(caps) == 6


def test_sql_identifier_rejects_injection() -> None:
    with pytest.raises(ValueError):
        assert_safe_sql_identifier("users; DROP TABLE users")
    with pytest.raises(ValueError):
        assert_safe_sql_identifier("a b")
    assert assert_safe_sql_identifier("orders_2024") == "orders_2024"


def test_url_blocks_loopback_by_default() -> None:
    with pytest.raises(ValueError, match="privado"):
        validate_http_url("http://127.0.0.1:8080/data")
    validate_http_url("http://127.0.0.1:8080/data", allow_private=True)


def test_file_connector_extract(tmp_path: Path) -> None:
    root = tmp_path / "src"
    root.mkdir()
    src = root / "sales.csv"
    src.write_text("a,b\n1,2\n3,4\n", encoding="utf-8")
    stage = tmp_path / "stage" / "out.csv"
    conn = get_connector("file")
    conn.validate_config({"root_path": str(root)})
    result = conn.extract(
        {"root_path": str(root)},
        None,
        stage_path=stage,
        object_id="sales.csv",
        mode="full",
    )
    assert result.size_bytes > 0
    assert stage.read_text(encoding="utf-8").startswith("a,b")


def test_rest_json_extract_with_mock(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    payload = {"items": [{"id": 1, "name": "x"}, {"id": 2, "name": "y"}]}

    def fake_request(method, url, **kwargs):  # noqa: ANN001
        req = httpx.Request(method, url)
        return httpx.Response(200, json=payload, request=req)

    transport = httpx.MockTransport(lambda request: fake_request(request.method, str(request.url)))

    real_client = httpx.Client

    def client_factory(*args, **kwargs):  # noqa: ANN002
        kwargs["transport"] = transport
        kwargs["follow_redirects"] = False
        return real_client(*args, **kwargs)

    monkeypatch.setattr(httpx, "Client", client_factory)

    # allow_private for mocked URL host resolution of example.com is fine —
    # use httpbin-like host that resolves publicly: we mock before request,
    # but validate_http_url still resolves DNS. Use allow_private + 127.0.0.1? 
    # Better: patch validate or use a public host.
    conn = get_connector("rest_json")
    config = {
        "base_url": "https://example.com",
        "path": "/api/items",
        "items_path": "items",
        "allowed_hosts": ["example.com"],
    }
    conn.validate_config(config)
    stage = tmp_path / "out.json"
    result = conn.extract(config, {"token": "sekrit"}, stage_path=stage, mode="sample", sample_limit=10)
    data = json.loads(stage.read_text(encoding="utf-8"))
    assert len(data) == 2
    assert result.format == "json"
