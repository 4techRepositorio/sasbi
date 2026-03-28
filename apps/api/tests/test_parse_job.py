"""TICKET-008 — job de parsing atualiza estado."""

from pathlib import Path

from sqlalchemy.orm import Session

from fourpro_api.jobs.ingestion_parse import run_ingestion_parse
from fourpro_api.repositories.ingestion_repository import IngestionRepository
from tests.test_auth import _bind_tenant, _create_user


def test_run_ingestion_parse_marks_processed(tmp_path: Path, db_session: Session) -> None:
    u = _create_user(db_session, "parse@example.com", "pw")
    tid = _bind_tenant(db_session, u)
    f = tmp_path / "sample.csv"
    f.write_text("h1,h2\n10,20\n", encoding="utf-8")
    repo = IngestionRepository(db_session)
    ing = repo.create(
        tenant_id=tid,
        original_filename="sample.csv",
        storage_path=str(f.resolve()),
        content_type="text/csv",
        size_bytes=f.stat().st_size,
        status="uploaded",
    )
    run_ingestion_parse(str(ing.id), db=db_session)
    again = repo.get_by_id(ing.id)
    assert again is not None
    assert again.status == "processed"
    assert again.result_summary is not None
