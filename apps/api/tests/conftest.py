import os
import tempfile
from collections.abc import Generator
from pathlib import Path

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("JWT_SECRET", "test-jwt-secret-at-least-32-characters-long")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "15")
os.environ.setdefault("REFRESH_TOKEN_EXPIRE_DAYS", "7")
_default_upl = Path(tempfile.gettempdir()) / "fourpro_api_pytest_uploads"
os.environ.setdefault("UPLOAD_DIR", str(_default_upl))
_default_upl.mkdir(parents=True, exist_ok=True)

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from fourpro_api.config import reset_settings_cache
from fourpro_api.db.base import Base
from fourpro_api.db.session import get_db, reset_db_engine
from fourpro_api.limiter import limiter
from fourpro_api.main import create_app


@pytest.fixture(autouse=True)
def _pytest_disable_rate_limits() -> Generator[None, None, None]:
    prev = limiter.enabled
    limiter.enabled = False
    yield
    limiter.enabled = prev


@pytest.fixture(autouse=True)
def _pytest_skip_parse_enqueue(monkeypatch: pytest.MonkeyPatch) -> None:
    """Evita Celery/sync parse com outra conexão SQLite nos testes (uploads)."""

    def _noop(_ingestion_id: str) -> None:
        return None

    monkeypatch.setattr("fourpro_api.routers.uploads.enqueue_ingestion_parse", _noop)


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    reset_settings_cache()
    reset_db_engine()
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"
    Path(os.environ["UPLOAD_DIR"]).mkdir(parents=True, exist_ok=True)

    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
        reset_db_engine()
        reset_settings_cache()


@pytest.fixture
def client(db_session: Session) -> Generator[TestClient, None, None]:
    app = create_app()

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
