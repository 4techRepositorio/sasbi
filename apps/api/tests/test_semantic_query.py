"""TICKET-016 — modelo semântico e query."""

import json
import uuid
from datetime import UTC, datetime
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from fourpro_api.models.ingestion import FileIngestion
from tests.test_auth import _bind_tenant, _create_user


def test_semantic_query_count(client: TestClient, db_session: Session, tmp_path: Path) -> None:
    u = _create_user(db_session, "sem@example.com", "pw")
    tid = _bind_tenant(db_session, u)
    data = {"rows": [{"region": "N", "amount": 10}, {"region": "S", "amount": 20}]}
    path = tmp_path / "data.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    now = datetime.now(tz=UTC)
    ds = FileIngestion(
        id=uuid.uuid4(),
        tenant_id=tid,
        original_filename="data.json",
        storage_path=str(path),
        size_bytes=path.stat().st_size,
        status="processed",
        layer="gold",
        created_at=now,
        updated_at=now,
    )
    db_session.add(ds)
    db_session.commit()
    token = client.post(
        "/api/v1/auth/login", json={"email": "sem@example.com", "password": "pw"}
    ).json()["access_token"]
    model = client.post(
        "/api/v1/semantic/models",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Vendas",
            "dataset_id": str(ds.id),
            "dimensions": [{"name": "region", "field": "region"}],
            "measures": [
                {"name": "count", "expression": "count"},
                {"name": "total", "expression": "sum", "field": "amount"},
            ],
        },
    )
    assert model.status_code == 201, model.text
    q = client.post(
        "/api/v1/query",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "semantic_model_id": model.json()["id"],
            "measures": ["count", "total"],
            "dimensions": ["region"],
        },
    )
    assert q.status_code == 200, q.text
    assert q.json()["layer"] == "gold"
    assert len(q.json()["rows"]) >= 1
