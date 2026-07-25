from fourpro_connectors import get_connector, list_connector_types
from fourpro_connectors.spi import ConnectorContext


def test_registry_has_o1() -> None:
    types = {c.type for c in list_connector_types()}
    assert types == {"file", "postgres", "rest_json"}


def test_file_extract_manifest() -> None:
    c = get_connector("file")
    assert c is not None
    r = c.extract(ConnectorContext(tenant_id="t", data_source_id="d", config={}))
    assert r.ok
    assert r.payload_bytes


def test_postgres_rejects_bad_table() -> None:
    c = get_connector("postgres")
    assert c is not None
    r = c.test_connection(
        ConnectorContext(
            tenant_id="t",
            data_source_id="d",
            config={"host": "h", "database": "db", "table": "bad;drop"},
            secret="u:p",
        )
    )
    assert not r.ok


def test_rest_blocks_without_allowlist_private() -> None:
    c = get_connector("rest_json")
    assert c is not None
    r = c.test_connection(
        ConnectorContext(
            tenant_id="t",
            data_source_id="d",
            config={"url": "http://127.0.0.1/secret"},
        )
    )
    assert not r.ok
