"""API — listagem, agregados e erros do modelo semântico."""

import json
import uuid
from datetime import UTC, datetime
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from fourpro_api.models.ingestion import FileIngestion
from fourpro_api.routers.semantic import _is_number, _load_rows
from tests.test_auth import _bind_tenant, _create_user


def _gold_ds(db: Session, tid, path: Path, payload: str | bytes) -> FileIngestion:
    if isinstance(payload, str):
        path.write_text(payload, encoding="utf-8")
    else:
        path.write_bytes(payload)
    now = datetime.now(tz=UTC)
    ds = FileIngestion(
        id=uuid.uuid4(),
        tenant_id=tid,
        original_filename=path.name,
        storage_path=str(path),
        size_bytes=path.stat().st_size,
        status="processed",
        layer="gold",
        created_at=now,
        updated_at=now,
    )
    db.add(ds)
    db.commit()
    return ds


@pytest.mark.unit
def test_load_rows_variants(tmp_path: Path) -> None:
    assert _load_rows(tmp_path / "missing.json") == []
    p_list = tmp_path / "list.json"
    p_list.write_text(json.dumps([{"a": 1}, "x"]), encoding="utf-8")
    assert _load_rows(p_list) == [{"a": 1}]
    p_items = tmp_path / "items.json"
    p_items.write_text(json.dumps({"items": [{"id": 1}]}), encoding="utf-8")
    assert _load_rows(p_items) == [{"id": 1}]
    p_obj = tmp_path / "obj.json"
    p_obj.write_text(json.dumps({"k": 1}), encoding="utf-8")
    assert _load_rows(p_obj) == [{"k": 1}]
    p_txt = tmp_path / "raw.txt"
    p_txt.write_text("not-json\nline2\n", encoding="utf-8")
    rows = _load_rows(p_txt)
    assert rows and "value" in rows[0]
    assert _is_number("3.5") is True
    assert _is_number("x") is False


@pytest.mark.integration
@pytest.mark.api
def test_semantic_list_global_avg_and_errors(
    client: TestClient, db_session: Session, tmp_path: Path
) -> None:
    u = _create_user(db_session, "semx@example.com", "pw")
    tid = _bind_tenant(db_session, u)
    ds = _gold_ds(
        db_session,
        tid,
        tmp_path / "sales.json",
        json.dumps({"rows": [{"region": "N", "amount": 10}, {"region": "S", "amount": 30}]}),
    )
    token = client.post(
        "/api/v1/auth/login", json={"email": "semx@example.com", "password": "pw"}
    ).json()["access_token"]
    h = {"Authorization": f"Bearer {token}"}

    bad = client.post(
        "/api/v1/semantic/models",
        headers=h,
        json={
            "name": "Bad",
            "dataset_id": str(uuid.uuid4()),
            "dimensions": [],
            "measures": [{"name": "count", "expression": "count"}],
        },
    )
    assert bad.status_code == 400

    model = client.post(
        "/api/v1/semantic/models",
        headers=h,
        json={
            "name": "Sales",
            "dataset_id": str(ds.id),
            "dimensions": [{"name": "region", "field": "region"}],
            "measures": [
                {"name": "count", "expression": "count"},
                {"name": "avg_amt", "expression": "avg", "field": "amount"},
            ],
        },
    )
    assert model.status_code == 201
    mid = model.json()["id"]

    listed = client.get("/api/v1/semantic/models", headers=h)
    assert listed.status_code == 200
    assert any(i["id"] == mid for i in listed.json()["items"])

    global_q = client.post(
        "/api/v1/query",
        headers=h,
        json={"semantic_model_id": mid, "measures": ["count", "avg_amt"], "dimensions": []},
    )
    assert global_q.status_code == 200
    assert global_q.json()["rows"][0][0] == 2
    assert global_q.json()["rows"][0][1] == 20.0

    missing = client.post(
        "/api/v1/query",
        headers=h,
        json={"semantic_model_id": str(uuid.uuid4()), "measures": ["count"], "dimensions": []},
    )
    assert missing.status_code == 404
