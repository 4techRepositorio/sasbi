from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, DateTime, ForeignKey, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from fourpro_api.db.base import Base

if TYPE_CHECKING:
    from fourpro_api.models.ingestion import FileIngestion
    from fourpro_api.models.tenant import Tenant


class SemanticModel(Base):
    """Modelo semântico por dataset (TICKET-016)."""

    __tablename__ = "semantic_models"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    dataset_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("file_ingestions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    description: Mapped[str | None] = mapped_column(Text(), nullable=True)
    fields_json: Mapped[list[dict[str, Any]]] = mapped_column(JSON, nullable=False, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    tenant: Mapped["Tenant"] = relationship("Tenant")
    dataset: Mapped["FileIngestion"] = relationship("FileIngestion")
