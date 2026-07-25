"""Conector `file` — ficheiros locais no stage/upload do tenant."""

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
from fourpro_connectors.plugins._io import infer_type, write_rows_csv, write_rows_json
from fourpro_connectors.registry import register

_ALLOWED_EXT = frozenset({".csv", ".txt", ".json", ".xlsx", ".xls"})


def _resolve_root(config: dict[str, Any]) -> Path:
    root = config.get("root_path") or config.get("base_path")
    if not root:
        raise ConnectorError("Config file exige root_path")
    p = Path(str(root)).resolve()
    if not p.is_dir():
        raise ConnectorError("root_path não é um diretório válido")
    return p


def _safe_rel(root: Path, object_id: str) -> Path:
    # Impede path traversal fora do root
    rel = object_id.lstrip("/").replace("\\", "/")
    if ".." in Path(rel).parts:
        raise ConnectorError("object_id inválido")
    target = (root / rel).resolve()
    try:
        target.relative_to(root)
    except ValueError as e:
        raise ConnectorError("object_id fora do root_path") from e
    return target


def _read_sample_rows(path: Path, limit: int) -> tuple[list[str], list[dict[str, Any]]]:
    import csv
    import json

    ext = path.suffix.lower()
    if ext in (".csv", ".txt"):
        with path.open(encoding="utf-8", errors="replace", newline="") as f:
            reader = csv.DictReader(f)
            cols = list(reader.fieldnames or [])
            rows: list[dict[str, Any]] = []
            for i, row in enumerate(reader):
                if i >= limit:
                    break
                rows.append(dict(row))
            return cols, rows
    if ext == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            data = [data]
        if not isinstance(data, list):
            raise ConnectorError("JSON deve ser objecto ou array")
        rows = [r for r in data[:limit] if isinstance(r, dict)]
        cols = list(rows[0].keys()) if rows else []
        return cols, rows
    raise ConnectorError(f"Amostra não suportada para extensão {ext}")


@register
class FileConnector(BaseConnector):
    connector_type = "file"

    def capabilities(self) -> ConnectorCapability:
        return ConnectorCapability(
            connector_type="file",
            display_name="Ficheiro",
            description="Ficheiros CSV/TXT/JSON/XLS no armazenamento do tenant",
            auth_kinds=["none"],
            supports_incremental=False,
            supports_discover=True,
            max_sample_rows=100,
            config_schema_hint={
                "root_path": "directory absolute path (server-side)",
                "default_object": "optional relative path",
            },
        )

    def validate_config(
        self,
        config: dict[str, Any],
        secret: dict[str, str] | None = None,
    ) -> None:
        _ = secret
        _resolve_root(config)

    def test_connection(
        self,
        config: dict[str, Any],
        secret: dict[str, str] | None = None,
    ) -> ConnectionTestResult:
        _ = secret
        try:
            root = _resolve_root(config)
        except ConnectorError as e:
            return ConnectionTestResult(ok=False, message=e.message)
        n = sum(1 for p in root.rglob("*") if p.is_file() and p.suffix.lower() in _ALLOWED_EXT)
        return ConnectionTestResult(
            ok=True,
            message="Diretório acessível",
            details={"root_path": str(root), "file_count": n},
        )

    def discover(
        self,
        config: dict[str, Any],
        secret: dict[str, str] | None = None,
    ) -> DiscoverResponse:
        _ = secret
        root = _resolve_root(config)
        objects: list[DiscoverObject] = []
        for p in sorted(root.rglob("*")):
            if not p.is_file() or p.suffix.lower() not in _ALLOWED_EXT:
                continue
            rel = str(p.relative_to(root)).replace("\\", "/")
            objects.append(
                DiscoverObject(object_id=rel, name=p.name, kind="file", meta={"size": p.stat().st_size})
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
        _ = secret
        root = _resolve_root(config)
        path = _safe_rel(root, object_id)
        if not path.is_file():
            raise ConnectorError("Ficheiro não encontrado")
        cols, rows = _read_sample_rows(path, limit)
        columns = [
            SchemaColumn(
                name=c,
                inferred_type=infer_type(rows[0].get(c)) if rows else "string",
                nullable=True,
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
        _ = secret
        root = _resolve_root(config)
        oid = object_id or config.get("default_object")
        if not oid:
            raise ConnectorError("object_id ou default_object é obrigatório")
        src = _safe_rel(root, str(oid))
        if not src.is_file():
            raise ConnectorError("Ficheiro fonte não encontrado")

        stage_path = Path(stage_path)
        stage_path.parent.mkdir(parents=True, exist_ok=True)
        ext = src.suffix.lower()

        if mode == "sample" and ext in (".csv", ".txt", ".json"):
            cols, rows = _read_sample_rows(src, sample_limit)
            if ext == ".json":
                write_rows_json(stage_path, rows)
                fmt: Literal["csv", "json"] = "json"
                ctype = "application/json"
            else:
                write_rows_csv(stage_path, rows, cols)
                fmt = "csv"
                ctype = "text/csv"
            size = stage_path.stat().st_size
            return ExtractResult(
                stage_path=stage_path.resolve(),
                format=fmt,
                original_filename=stage_path.name,
                content_type=ctype,
                size_bytes=size,
                row_count=len(rows),
                object_id=str(oid),
                meta={"source": str(src)},
            )

        # full: copy bytes (xlsx etc. inclusive)
        data = src.read_bytes()
        stage_path.write_bytes(data)
        if ext == ".json":
            fmt2: Literal["csv", "json"] = "json"
            ctype2 = "application/json"
        elif ext in (".csv", ".txt"):
            fmt2 = "csv"
            ctype2 = "text/csv"
        else:
            fmt2 = "csv"
            ctype2 = "application/octet-stream"
        return ExtractResult(
            stage_path=stage_path.resolve(),
            format=fmt2,
            original_filename=src.name,
            content_type=ctype2,
            size_bytes=len(data),
            row_count=None,
            object_id=str(oid),
            meta={"source": str(src)},
        )
