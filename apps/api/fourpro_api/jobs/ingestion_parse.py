import csv
import json
import logging
from pathlib import Path
from uuid import UUID

from sqlalchemy.orm import Session

from fourpro_api.config import get_settings
from fourpro_api.db.session import get_session_maker
from fourpro_api.repositories.ingestion_repository import IngestionRepository
from fourpro_api.services.upload_validation import UploadContentError, validate_upload_content

logger = logging.getLogger(__name__)

_MAX_TEXT_SCAN = 20_000_000


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

        disk_size = path.stat().st_size
        if disk_size != row.size_bytes:
            repo.update(
                row,
                status="failed",
                friendly_error="O arquivo no servidor não coincide com o registo de upload",
                technical_log=f"size_bytes_db={row.size_bytes} size_on_disk={disk_size}",
            )
            return

        settings = get_settings()
        max_b = settings.max_upload_mb * 1024 * 1024
        if disk_size > max_b:
            repo.update(
                row,
                status="failed",
                friendly_error="Arquivo excede o tamanho máximo permitido",
                technical_log=f"size={disk_size} max={max_b}",
            )
            return

        body = path.read_bytes()
        try:
            validate_upload_content(declared_name=row.original_filename, body=body)
        except UploadContentError as e:
            repo.update(
                row,
                status="failed",
                friendly_error=str(e),
                technical_log=f"validation_failed: {e}",
            )
            return

        ext = path.suffix.lower().lstrip(".")
        try:
            repo.update(row, status="parsing")
            if ext in ("csv", "txt"):
                text = body.decode("utf-8", errors="replace")
                if len(text) > _MAX_TEXT_SCAN:
                    text = text[:_MAX_TEXT_SCAN]
                if ext == "csv":
                    reader = csv.reader(text.splitlines())
                    n = sum(1 for _ in reader)
                    summary = f"csv_rows_estimated={n}"
                else:
                    summary = f"txt_len={len(text)}"
            elif ext == "json":
                data = json.loads(body.decode("utf-8", errors="strict"))
                if isinstance(data, dict):
                    summary = f"json_keys={len(data)}"
                elif isinstance(data, list):
                    summary = f"json_list_len={len(data)}"
                else:
                    summary = "json_scalar"
            elif ext in ("xlsx", "xls"):
                try:
                    from fourpro_shared.spreadsheet import (
                        SpreadsheetSummaryError,
                        summarize_workbook,
                    )

                    summary = summarize_workbook(path)
                except SpreadsheetSummaryError as e:
                    repo.update(
                        row,
                        status="failed",
                        friendly_error="Não foi possível ler a folha de cálculo",
                        technical_log=str(e),
                    )
                    return
                except Exception as e:
                    logger.exception(
                        "spreadsheet_parse_error", extra={"ingestion_id": ingestion_id}
                    )
                    repo.update(
                        row,
                        status="failed",
                        friendly_error="Erro ao ler XLS/XLSX",
                        technical_log=str(e),
                    )
                    return
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
