import logging
from pathlib import Path
from uuid import UUID

from sqlalchemy.orm import Session

from fourpro_api.config import get_settings
from fourpro_api.db.session import get_session_maker
from fourpro_api.repositories.ingestion_repository import IngestionRepository
from fourpro_api.services.tabular_extract import extract_tabular_rows
from fourpro_api.services.upload_validation import UploadContentError, validate_upload_content

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

        repo.update(row, status="validating", parsed_rows_json=None)
        path = Path(row.storage_path)
        if not path.exists():
            repo.update(
                row,
                status="failed",
                friendly_error="Arquivo não encontrado no storage",
                technical_log=f"missing path {path}",
                parsed_rows_json=None,
            )
            return

        disk_size = path.stat().st_size
        if disk_size != row.size_bytes:
            repo.update(
                row,
                status="failed",
                friendly_error="O arquivo no servidor não coincide com o registo de upload",
                technical_log=f"size_bytes_db={row.size_bytes} size_on_disk={disk_size}",
                parsed_rows_json=None,
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
                parsed_rows_json=None,
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
                parsed_rows_json=None,
            )
            return

        try:
            repo.update(row, status="parsing")
            try:
                rows, summary, _truncated = extract_tabular_rows(path, body=body)
            except ValueError as e:
                repo.update(
                    row,
                    status="failed",
                    friendly_error="Tipo não suportado nesta versão",
                    technical_log=str(e),
                    parsed_rows_json=None,
                )
                return
            except Exception as e:
                logger.exception("tabular_extract_error", extra={"ingestion_id": ingestion_id})
                repo.update(
                    row,
                    status="failed",
                    friendly_error="Erro ao processar o arquivo",
                    technical_log=str(e),
                    parsed_rows_json=None,
                )
                return

            repo.update(
                row,
                status="processed",
                result_summary=summary,
                parsed_rows_json=rows,
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
                parsed_rows_json=None,
            )
    finally:
        if own_session:
            db.close()
