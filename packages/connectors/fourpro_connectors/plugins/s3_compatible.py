"""Conector S3-compatible (MinIO / AWS S3)."""

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
from fourpro_connectors.plugins._io import infer_type
from fourpro_connectors.registry import register
from fourpro_connectors.security import validate_http_url


def _client(config: dict[str, Any], secret: dict[str, str] | None):
    try:
        import boto3
        from botocore.client import Config as BotoConfig
    except ImportError as e:
        raise ConnectorError(
            "Cliente S3 não instalado (boto3)",
            technical="pip install boto3",
        ) from e
    endpoint = config.get("endpoint_url")
    bucket = config.get("bucket")
    if not bucket:
        raise ConnectorError("Config s3_compatible exige bucket")
    if endpoint:
        validate_http_url(
            str(endpoint),
            allow_private=bool(config.get("allow_private_hosts") is True),
            allowed_hosts=config.get("allowed_hosts"),
        )
    secret = secret or {}
    access = secret.get("access_key") or secret.get("access_key_id")
    secret_key = secret.get("secret_key") or secret.get("secret_access_key")
    if not access or not secret_key:
        raise ConnectorError("Credenciais access_key e secret_key obrigatórias")
    return boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=access,
        aws_secret_access_key=secret_key,
        region_name=config.get("region") or "us-east-1",
        config=BotoConfig(signature_version="s3v4"),
    ), str(bucket)


@register
class S3CompatibleConnector(BaseConnector):
    connector_type = "s3_compatible"

    def capabilities(self) -> ConnectorCapability:
        return ConnectorCapability(
            connector_type="s3_compatible",
            display_name="Object storage (S3-compatible)",
            description="Buckets S3 / MinIO — listagem e download de objectos",
            auth_kinds=["aws_sig_v4"],
            supports_incremental=False,
            supports_discover=True,
            max_sample_rows=50,
            config_schema_hint={
                "endpoint_url": "http://minio:9000",
                "bucket": "string",
                "prefix": "",
                "region": "us-east-1",
                "allow_private_hosts": False,
            },
        )

    def validate_config(
        self,
        config: dict[str, Any],
        secret: dict[str, str] | None = None,
    ) -> None:
        if not config.get("bucket"):
            raise ConnectorError("bucket é obrigatório")
        endpoint = config.get("endpoint_url")
        if endpoint:
            validate_http_url(
                str(endpoint),
                allow_private=bool(config.get("allow_private_hosts") is True),
                allowed_hosts=config.get("allowed_hosts"),
            )
        _ = secret

    def test_connection(
        self,
        config: dict[str, Any],
        secret: dict[str, str] | None = None,
    ) -> ConnectionTestResult:
        try:
            client, bucket = _client(config, secret)
            client.head_bucket(Bucket=bucket)
            return ConnectionTestResult(ok=True, message="Bucket acessível")
        except ConnectorError as e:
            return ConnectionTestResult(ok=False, message=e.message)
        except Exception as e:  # noqa: BLE001
            return ConnectionTestResult(
                ok=False, message="Falha ao aceder ao bucket", details={"error": type(e).__name__}
            )

    def discover(
        self,
        config: dict[str, Any],
        secret: dict[str, str] | None = None,
    ) -> DiscoverResponse:
        client, bucket = _client(config, secret)
        prefix = str(config.get("prefix") or "")
        resp = client.list_objects_v2(Bucket=bucket, Prefix=prefix, MaxKeys=200)
        objects: list[DiscoverObject] = []
        for obj in resp.get("Contents") or []:
            key = obj["Key"]
            objects.append(
                DiscoverObject(
                    object_id=key,
                    name=key.rsplit("/", 1)[-1],
                    kind="object",
                    meta={"size": obj.get("Size"), "bucket": bucket},
                )
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
        # Para objectos textuais CSV/JSON — amostra após download temporário
        import csv
        import json
        import tempfile

        client, bucket = _client(config, secret)
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            client.download_fileobj(bucket, object_id, tmp)
            tmp_path = Path(tmp.name)
        try:
            ext = Path(object_id).suffix.lower()
            rows: list[dict[str, Any]] = []
            cols: list[str] = []
            if ext in (".csv", ".txt"):
                with tmp_path.open(encoding="utf-8", errors="replace", newline="") as f:
                    reader = csv.DictReader(f)
                    cols = list(reader.fieldnames or [])
                    for i, row in enumerate(reader):
                        if i >= limit:
                            break
                        rows.append(dict(row))
            elif ext == ".json":
                data = json.loads(tmp_path.read_text(encoding="utf-8"))
                if isinstance(data, dict):
                    data = [data]
                rows = [r for r in data[:limit] if isinstance(r, dict)]
                cols = list(rows[0].keys()) if rows else []
            else:
                return SampleSchemaResponse(
                    object_id=object_id,
                    columns=[SchemaColumn(name="bytes", inferred_type="binary")],
                    sample_rows=[],
                )
            columns = [
                SchemaColumn(
                    name=c,
                    inferred_type=infer_type(rows[0].get(c)) if rows else "string",
                )
                for c in cols
            ]
            return SampleSchemaResponse(object_id=object_id, columns=columns, sample_rows=rows)
        finally:
            tmp_path.unlink(missing_ok=True)

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
        _ = mode, sample_limit
        oid = object_id or config.get("default_object") or config.get("key")
        if not oid:
            raise ConnectorError("object_id (key) é obrigatório")
        client, bucket = _client(config, secret)
        stage_path = Path(stage_path)
        stage_path.parent.mkdir(parents=True, exist_ok=True)
        with stage_path.open("wb") as f:
            client.download_fileobj(bucket, str(oid), f)
        size = stage_path.stat().st_size
        ext = Path(str(oid)).suffix.lower()
        if ext == ".json":
            fmt: Literal["csv", "json"] = "json"
            ctype = "application/json"
        elif ext in (".csv", ".txt"):
            fmt = "csv"
            ctype = "text/csv"
        else:
            fmt = "csv"
            ctype = "application/octet-stream"
        return ExtractResult(
            stage_path=stage_path.resolve(),
            format=fmt,
            original_filename=Path(str(oid)).name,
            content_type=ctype,
            size_bytes=size,
            row_count=None,
            object_id=str(oid),
            meta={"bucket": bucket},
        )
