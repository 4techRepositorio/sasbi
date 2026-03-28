import csv
import json
import logging
from pathlib import Path
from uuid import UUID

from sqlalchemy.orm import Session

from fourpro_api.db.session import get_session_maker
from fourpro_api.repositories.ingestion_repository import IngestionRepository

logger = logging.getLogger(__name__)


def run_ingestion_parse(ingestion_id: str, *, db: Session | None = None) -> None:
    own_session = db is None
    if own_session:
        sm = get_session_maker()
        db = sm()
    assert db is not None
    try:
        repo = IngestionRepository(db)
        row = repo.get_by_id(UUID(ingestion_id))
        if row is None:
            logger.warning("ingestion_not_found", extra={"id": ingestion_id})
            return

        repo.update(row, status="validating")
        path = Path(row.storage_path)
        if not path.exists():
            repo.update(
                row,
                status="failed",
                friendly_error="Arquivo não encontrado no storage",
                technical_log=f"missing path {path}",
            )
            return

        ext = path.suffix.lower().lstrip(".")
        try:
            repo.update(row, status="parsing")
            if ext in ("csv", "txt"):
                with path.open(encoding="utf-8", errors="replace") as f:
                    text = f.read(20_000_000)
                if ext == "csv":
                    reader = csv.reader(text.splitlines())
                    n = sum(1 for _ in reader)
                    summary = f"csv_rows_estimated={n}"
                else:
                    summary = f"txt_len={len(text)}"
            elif ext == "json":
                data = json.loads(path.read_text(encoding="utf-8", errors="replace"))
                if isinstance(data, dict):
                    summary = f"json_keys={len(data)}"
                elif isinstance(data, list):
                    summary = f"json_list_len={len(data)}"
                else:
                    summary = "json_scalar"
            elif ext in ("xlsx", "xls"):
                summary = "xlsx_parsing_stub_mark_processed"
            else:
                repo.update(
                    row,
                    status="failed",
                    friendly_error="Tipo não suportado nesta versão",
                    technical_log=f"ext={ext}",
                )
                return

            repo.update(
                row,
                status="processed",
                result_summary=summary,
                technical_log=None,
                friendly_error=None,
            )
        except Exception as e:
            logger.exception("parse_error", extra={"ingestion_id": ingestion_id})
            repo.update(
                row,
                status="failed",
                friendly_error="Erro ao processar o arquivo",
                technical_log=str(e),
            )
    finally:
        if own_session:
            db.close()
