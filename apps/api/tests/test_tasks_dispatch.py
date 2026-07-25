"""Unitários — dispatch Celery / fallback sync de parse."""

from unittest.mock import MagicMock

import pytest

from fourpro_api import tasks_dispatch
from fourpro_api.config import reset_settings_cache


@pytest.mark.unit
@pytest.mark.ingestion
def test_sync_fallback_runs_parse(monkeypatch) -> None:
    called: list[str] = []

    monkeypatch.setenv("INGESTION_SYNC_PARSE_FALLBACK", "1")
    monkeypatch.setenv("REDIS_URL", "")
    reset_settings_cache()
    tasks_dispatch._celery_app = None

    monkeypatch.setattr(
        "fourpro_api.jobs.ingestion_parse.run_ingestion_parse",
        lambda ingestion_id: called.append(ingestion_id),
    )

    tasks_dispatch.enqueue_ingestion_parse("ing-1")
    assert called == ["ing-1"]
    reset_settings_cache()


@pytest.mark.unit
@pytest.mark.ingestion
def test_celery_enqueue_when_redis_configured(monkeypatch) -> None:
    monkeypatch.delenv("INGESTION_SYNC_PARSE_FALLBACK", raising=False)
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")
    reset_settings_cache()
    tasks_dispatch._celery_app = None

    mock_app = MagicMock()
    monkeypatch.setattr(tasks_dispatch, "_get_celery_app", lambda _url: mock_app)

    tasks_dispatch.enqueue_ingestion_parse("ing-celery")
    mock_app.send_task.assert_called_once_with(
        "fourpro.parse_ingestion",
        args=["ing-celery"],
    )
    reset_settings_cache()
    tasks_dispatch._celery_app = None


@pytest.mark.unit
@pytest.mark.ingestion
def test_get_celery_app_caches_instance(monkeypatch) -> None:
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")
    reset_settings_cache()
    tasks_dispatch._celery_app = None
    a = tasks_dispatch._get_celery_app("redis://localhost:6379/0")
    b = tasks_dispatch._get_celery_app("redis://localhost:6379/0")
    assert a is b
    tasks_dispatch._celery_app = None
    reset_settings_cache()


@pytest.mark.unit
@pytest.mark.ingestion
def test_celery_failure_falls_back_to_sync(monkeypatch) -> None:
    called: list[str] = []
    monkeypatch.setenv("INGESTION_SYNC_PARSE_FALLBACK", "true")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")
    reset_settings_cache()
    tasks_dispatch._celery_app = None

    mock_app = MagicMock()
    mock_app.send_task.side_effect = RuntimeError("broker down")
    monkeypatch.setattr(tasks_dispatch, "_get_celery_app", lambda _url: mock_app)
    monkeypatch.setattr(
        "fourpro_api.jobs.ingestion_parse.run_ingestion_parse",
        lambda ingestion_id: called.append(ingestion_id),
    )

    tasks_dispatch.enqueue_ingestion_parse("ing-fb")
    assert called == ["ing-fb"]
    reset_settings_cache()
    tasks_dispatch._celery_app = None
