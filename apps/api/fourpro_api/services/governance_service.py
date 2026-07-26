"""Promoção de camadas bronze/silver/gold (TICKET-012)."""

from __future__ import annotations

import shutil
from pathlib import Path
from uuid import UUID, uuid4

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from fourpro_api.config import get_settings
from fourpro_api.middleware.correlation import get_correlation_id
from fourpro_api.repositories.audit_repository import AuditAction, AuditRepository
from fourpro_api.repositories.ingestion_repository import IngestionRepository

_ORDER = {"bronze": 0, "silver": 1, "gold": 2}


class GovernanceService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._ingestions = IngestionRepository(db)
        self._audit = AuditRepository(db)

    def promote(
        self,
        *,
        tenant_id: UUID,
        actor_user_id: UUID,
        source_id: UUID,
        target_layer: str,
        transform_version: str,
    ):
        src = self._ingestions.get(source_id, tenant_id)
        if src is None or src.status != "processed":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dataset processado não encontrado neste tenant",
            )
        if _ORDER.get(target_layer, -1) <= _ORDER.get(src.layer, 0):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A camada alvo deve ser superior à actual (bronze→silver→gold)",
            )
        settings = get_settings()
        src_path = Path(src.storage_path)
        if not src_path.is_file():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ficheiro fonte indisponível para promoção",
            )
        dest_dir = Path(settings.upload_dir) / str(tenant_id) / "promoted"
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / f"{uuid4()}_{src_path.name}"
        try:
            shutil.copy2(src_path, dest)
        except OSError as exc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Falha ao materializar camada",
            ) from exc

        cid = get_correlation_id()
        new_row = self._ingestions.create(
            tenant_id=tenant_id,
            original_filename=f"{target_layer}__{src.original_filename}",
            storage_path=str(dest.resolve()),
            content_type=src.content_type,
            size_bytes=src.size_bytes,
            status="processed",
            content_sha256=src.content_sha256,
            uploaded_by_user_id=actor_user_id,
            layer=target_layer,
            source_ingestion_id=src.id,
            transform_version=transform_version,
            correlation_id=cid,
            result_summary=f"Promovido de {src.layer} → {target_layer} ({transform_version})",
            technical_log=(
                f"promote source={src.id} target={target_layer} "
                f"version={transform_version}"
            ),
        )
        self._audit.record(
            action=AuditAction.DATASET_PROMOTED,
            actor_user_id=actor_user_id,
            tenant_id=tenant_id,
            context={
                "source_ingestion_id": str(src.id),
                "new_ingestion_id": str(new_row.id),
                "layer": target_layer,
                "transform_version": transform_version,
            },
        )
        return new_row
