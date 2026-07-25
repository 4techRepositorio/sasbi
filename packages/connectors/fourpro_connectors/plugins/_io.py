"""Utilitários partilhados de extract (CSV/JSON para stage)."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


def write_rows_csv(path: Path, rows: list[dict[str, Any]], columns: list[str] | None = None) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows and not columns:
        path.write_text("", encoding="utf-8")
        return 0
    cols = columns or list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({c: row.get(c) for c in cols})
    return len(rows)


def write_rows_json(path: Path, rows: list[dict[str, Any]]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(rows, ensure_ascii=False, default=str), encoding="utf-8")
    return len(rows)


def infer_type(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int) and not isinstance(value, bool):
        return "integer"
    if isinstance(value, float):
        return "number"
    return "string"
