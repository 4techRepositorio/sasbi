from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, BigInteger, DateTime, ForeignKey, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from fourpro_api.db.base import Base

if TYPE_CHECKING:
    from fourpro_api.models.tenant import Tenant

# Limite de linhas tabulares persistidas para o motor de query (TICKET-016).
PARSED_ROWS_CAP = 50_000


class FileIngestion(Base):
    __tablename__ = "file_ingestions"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    original_filename: Mapped[str] = mapped_column(String(512), nullable=False)
    storage_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    content_type: Mapped[str | None] = mapped_column(String(255), nullable=True)
    content_sha256: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    uploaded_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    size_bytes: Mapped[int] = mapped_column(BigInteger(), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="uploaded")
    friendly_error: Mapped[str | None] = mapped_column(Text(), nullable=True)
    technical_log: Mapped[str | None] = mapped_column(Text(), nullable=True)
    result_summary: Mapped[str | None] = mapped_column(Text(), nullable=True)
    parsed_rows_json: Mapped[list[dict[str, Any]] | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    tenant: Mapped["Tenant"] = relationship("Tenant", back_populates="ingestions")
