"""Cobertura adicional do job de parse (oversize, JSON list, spreadsheet mock)."""

from pathlib import Path
from unittest.mock import patch

import pytest
from sqlalchemy.orm import Session

from fourpro_api.config import reset_settings_cache
from fourpro_api.jobs.ingestion_parse import run_ingestion_parse
from fourpro_api.repositories.ingestion_repository import IngestionRepository
from tests.test_auth import _bind_tenant, _create_user


def _ing(db: Session, tmp_path: Path, name: str, body: bytes):
    u = _create_user(db, f"px-{name.replace('.', '-')}@example.com", "pw")
    tid = _bind_tenant(db, u)
    path = tmp_path / name
    path.write_bytes(body)
    repo = IngestionRepository(db)
    ing = repo.create(
        tenant_id=tid,
        original_filename=name,
        storage_path=str(path.resolve()),
        content_type="application/octet-stream",
        size_bytes=path.stat().st_size,
        status="uploaded",
    )
    return repo, ing


@pytest.mark.integration
@pytest.mark.ingestion
def test_parse_rejects_over_max_upload_mb(tmp_path: Path, db_session: Session, monkeypatch) -> None:
    monkeypatch.setenv("MAX_UPLOAD_MB", "1")
    reset_settings_cache()
    body = b"c\n" + (b"0\n" * 600_000)
    repo, ing = _ing(db_session, tmp_path, "huge.csv", body)
    run_ingestion_parse(str(ing.id), db=db_session)
    again = repo.get_by_id(ing.id)
    assert again is not None
    assert again.status == "failed"
    assert "tamanho" in (again.friendly_error or "").lower()
    reset_settings_cache()


@pytest.mark.integration
@pytest.mark.ingestion
def test_parse_json_list_summary(tmp_path: Path, db_session: Session) -> None:
    repo, ing = _ing(db_session, tmp_path, "arr.json", b"[1,2,3]")
    run_ingestion_parse(str(ing.id), db=db_session)
    row = repo.get_by_id(ing.id)
    assert row is not None
    assert row.status == "processed"
    assert "json_list_len=3" in (row.result_summary or "")


@pytest.mark.integration
@pytest.mark.ingestion
def test_parse_xlsx_via_shared_mock(tmp_path: Path, db_session: Session) -> None:
    body = b"PK\x03\x04" + b"\x00" * 32
    repo, ing = _ing(db_session, tmp_path, "sheet.xlsx", body)
    with patch(
        "fourpro_shared.spreadsheet.summarize_workbook",
        return_value="xlsx_sheets=1",
    ):
        run_ingestion_parse(str(ing.id), db=db_session)
    row = repo.get_by_id(ing.id)
    assert row is not None
    assert row.status == "processed"
    assert row.result_summary == "xlsx_sheets=1"
