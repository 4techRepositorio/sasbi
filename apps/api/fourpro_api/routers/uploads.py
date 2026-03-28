import hashlib
import re
import uuid
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, status
from fourpro_contracts.ingestion import UploadCreatedResponse
from sqlalchemy.orm import Session

from fourpro_api.config import get_settings
from fourpro_api.core.principal import Principal
from fourpro_api.db.session import get_db
from fourpro_api.dependencies.auth import require_roles
from fourpro_api.limiter import limiter
from fourpro_api.repositories.ingestion_repository import IngestionRepository
from fourpro_api.services.billing_service import BillingService
from fourpro_api.services.upload_validation import UploadContentError, validate_upload_content
from fourpro_api.tasks_dispatch import enqueue_ingestion_parse

router = APIRouter(prefix="/uploads", tags=["uploads"])

_SAFE_NAME = re.compile(r"[^a-zA-Z0-9._-]+")


def _safe_filename(name: str | None) -> str:
    if not name:
        return "file"
    base = Path(name).name
    return _SAFE_NAME.sub("_", base)[:200] or "file"


@router.post(
    "",
    summary="Upload inicial de arquivo (TICKET-006)",
    response_model=UploadCreatedResponse,
)
@limiter.limit("60/minute")
async def create_upload(
    request: Request,
    principal: Annotated[Principal, Depends(require_roles("admin", "analyst"))],
    db: Annotated[Session, Depends(get_db)],
    file: UploadFile,
) -> UploadCreatedResponse:
    settings = get_settings()
    billing = BillingService(db)
    billing.ensure_upload_allowed(principal.tenant_id)

    raw = file.filename or "upload"
    ext = Path(raw).suffix.lower().lstrip(".")
    allowed = {"csv", "txt", "json", "xlsx", "xls"}
    if ext not in allowed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "Tipo não permitido", "allowed": sorted(allowed)},
        )

    body = await file.read()
    max_b = settings.max_upload_mb * 1024 * 1024
    if len(body) > max_b:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Arquivo acima do limite de {settings.max_upload_mb} MB",
        )

    billing.ensure_storage_for_new_upload(principal.tenant_id, principal.user_id, len(body))

    try:
        validate_upload_content(declared_name=raw, body=body)
    except UploadContentError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e

    content_sha256 = hashlib.sha256(body).hexdigest()

    base_dir = Path(settings.upload_dir) / str(principal.tenant_id)
    base_dir.mkdir(parents=True, exist_ok=True)
    uid = uuid.uuid4()
    safe = _safe_filename(file.filename)
    dest = base_dir / f"{uid}_{safe}"
    dest.write_bytes(body)

    repo = IngestionRepository(db)
    ing = repo.create(
        tenant_id=principal.tenant_id,
        original_filename=raw,
        storage_path=str(dest.resolve()),
        content_type=file.content_type,
        size_bytes=len(body),
        status="uploaded",
        content_sha256=content_sha256,
        uploaded_by_user_id=principal.user_id,
    )

    enqueue_ingestion_parse(str(ing.id))

    return UploadCreatedResponse(
        id=str(ing.id),
        tenant_id=str(ing.tenant_id),
        status=ing.status,
        original_filename=ing.original_filename,
        size_bytes=ing.size_bytes,
        content_type=ing.content_type,
        content_sha256=content_sha256,
        uploaded_by_user_id=str(principal.user_id),
        created_at=ing.created_at.isoformat(),
    )
