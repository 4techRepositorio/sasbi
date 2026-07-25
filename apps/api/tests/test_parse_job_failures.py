"""Integração — falhas do job de parse (ficheiro, tamanho, validação, formatos)."""

from pathlib import Path

import pytest
from sqlalchemy.orm import Session

from fourpro_api.jobs.ingestion_parse import run_ingestion_parse
from fourpro_api.repositories.ingestion_repository import IngestionRepository
from tests.test_auth import _bind_tenant, _create_user


def _seed_ingestion(
    db: Session,
    tmp_path: Path,
    *,
    name: str,
    body: bytes | None,
    size_bytes: int | None = None,
    write_file: bool = True,
):
    u = _create_user(db, f"parse-{name}@example.com", "pw")
    tid = _bind_tenant(db, u)
    path = tmp_path / name
    if write_file and body is not None:
        path.write_bytes(body)
        disk = path.stat().st_size
    else:
        disk = size_bytes or 0
    repo = IngestionRepository(db)
    ing = repo.create(
        tenant_id=tid,
        original_filename=name,
        storage_path=str(path.resolve()),
        content_type="application/octet-stream",
        size_bytes=size_bytes if size_bytes is not None else disk,
        status="uploaded",
    )
    return repo, ing


@pytest.mark.integration
@pytest.mark.ingestion
def test_parse_missing_file_fails(tmp_path: Path, db_session: Session) -> None:
    repo, ing = _seed_ingestion(
        db_session,
        tmp_path,
        name="gone.csv",
        body=None,
        size_bytes=10,
        write_file=False,
    )
    run_ingestion_parse(str(ing.id), db=db_session)
    again = repo.get_by_id(ing.id)
    assert again is not None
    assert again.status == "failed"
    assert again.friendly_error


@pytest.mark.integration
@pytest.mark.ingestion
def test_parse_size_mismatch_fails(tmp_path: Path, db_session: Session) -> None:
    repo, ing = _seed_ingestion(
        db_session,
        tmp_path,
        name="mismatch.csv",
        body=b"a\n1\n",
        size_bytes=9999,
    )
    run_ingestion_parse(str(ing.id), db=db_session)
    again = repo.get_by_id(ing.id)
    assert again is not None
    assert again.status == "failed"
    assert "coincide" in (again.friendly_error or "").lower()


@pytest.mark.integration
@pytest.mark.ingestion
@pytest.mark.security
def test_parse_validation_failure(tmp_path: Path, db_session: Session) -> None:
    body = b"\xff\xfe binary"
    repo, ing = _seed_ingestion(db_session, tmp_path, name="bad.csv", body=body)
    run_ingestion_parse(str(ing.id), db=db_session)
    again = repo.get_by_id(ing.id)
    assert again is not None
    assert again.status == "failed"


@pytest.mark.integration
@pytest.mark.ingestion
def test_parse_json_and_txt_success(tmp_path: Path, db_session: Session) -> None:
    repo_j, ing_j = _seed_ingestion(
        db_session,
        tmp_path,
        name="ok.json",
        body=b'{"x":1,"y":2}',
    )
    run_ingestion_parse(str(ing_j.id), db=db_session)
    assert repo_j.get_by_id(ing_j.id).status == "processed"

    repo_t, ing_t = _seed_ingestion(
        db_session,
        tmp_path,
        name="ok.txt",
        body=b"hello world\n",
    )
    run_ingestion_parse(str(ing_t.id), db=db_session)
    row = repo_t.get_by_id(ing_t.id)
    assert row is not None
    assert row.status == "processed"
    assert "txt_len" in (row.result_summary or "")


@pytest.mark.integration
@pytest.mark.ingestion
def test_parse_unknown_ingestion_id_noop(db_session: Session) -> None:
    run_ingestion_parse("00000000-0000-0000-0000-000000000099", db=db_session)
