"""Performance / concorrência — smokes leves (não stress de produção)."""

import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from fourpro_api.services.upload_validation import validate_upload_content
from tests.test_auth import _bind_tenant, _create_user


@pytest.mark.performance
@pytest.mark.api
def test_health_latency_budget(client: TestClient) -> None:
    # Warm-up
    client.get("/api/v1/health")
    start = time.perf_counter()
    for _ in range(40):
        r = client.get("/api/v1/health")
        assert r.status_code == 200
    elapsed = time.perf_counter() - start
    assert elapsed < 2.0, f"40 health em {elapsed:.3f}s (orçamento 2s)"


@pytest.mark.concurrency
@pytest.mark.unit
def test_concurrent_upload_validation() -> None:
    payloads = [(f"f{i}.csv", b"a,b\n1,2\n") for i in range(20)] + [
        ("o.json", b'{"ok":true}'),
        ("t.txt", b"hello"),
    ]

    def _one(item: tuple[str, bytes]) -> None:
        validate_upload_content(declared_name=item[0], body=item[1])

    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = [pool.submit(_one, p) for p in payloads]
        for f in as_completed(futures):
            f.result()


@pytest.mark.concurrency
@pytest.mark.api
def test_parallel_health_smoke(client: TestClient) -> None:
    """Health é read-only; login paralelo partilhava Session e corrompia o flush."""

    def health() -> int:
        return client.get("/api/v1/health").status_code

    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = [pool.submit(health) for _ in range(24)]
        codes = [f.result() for f in as_completed(futures)]
    assert all(c == 200 for c in codes), codes


@pytest.mark.api
@pytest.mark.auth
def test_sequential_login_burst_ok(client: TestClient, db_session: Session) -> None:
    u = _create_user(db_session, "perf@example.com", "secretpass123")
    _bind_tenant(db_session, u)
    for _ in range(5):
        r = client.post(
            "/api/v1/auth/login",
            json={"email": "perf@example.com", "password": "secretpass123"},
        )
        assert r.status_code == 200
        assert r.json().get("access_token")
