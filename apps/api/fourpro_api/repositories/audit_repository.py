from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from fourpro_api.middleware.correlation import get_correlation_id
from fourpro_api.models.audit_log import AuditLog


class AuditAction:
    AUTH_SESSION_ISSUED = "auth.session.issued"
    AUTH_LOGIN_FAILED = "auth.login.failed"
    AUTH_MFA_CHALLENGE_SENT = "auth.mfa.challenge_sent"
    AUTH_TOKEN_REFRESH = "auth.token.refresh"
    AUTH_PASSWORD_RESET_REQUESTED = "auth.password_reset.requested"
    AUTH_PASSWORD_RESET_COMPLETED = "auth.password_reset.completed"
    TENANT_MEMBERS_LISTED = "tenant.members.listed"
    TENANT_QUOTA_GROUP_CREATED = "tenant.quota_group.created"
    TENANT_QUOTA_GROUP_UPDATED = "tenant.quota_group.updated"
    TENANT_QUOTA_GROUP_DELETED = "tenant.quota_group.deleted"
    TENANT_MEMBER_QUOTAS_UPDATED = "tenant.member.quotas_updated"
    UPLOAD_CREATED = "upload.created"
    INGESTION_STATUS_CHANGED = "ingestion.status_changed"
    DATASET_PROMOTED = "dataset.promoted"
    DASHBOARD_CREATED = "dashboard.created"
    DASHBOARD_UPDATED = "dashboard.updated"
    DASHBOARD_DELETED = "dashboard.deleted"
    DATA_SOURCE_CREATED = "data_source.created"
    DATA_SOURCE_TESTED = "data_source.tested"
    DATA_SOURCE_SYNC_ENQUEUED = "data_source.sync_enqueued"
    SEMANTIC_MODEL_CREATED = "semantic_model.created"
    DESKTOP_DATASET_PUBLISHED = "desktop.dataset.published"
    DESKTOP_DASHBOARD_PUBLISHED = "desktop.dashboard.published"


class AuditRepository:
    """Apenas inserções — sem updates/deletes na app."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def record(
        self,
        *,
        action: str,
        actor_user_id: UUID | None = None,
        tenant_id: UUID | None = None,
        context: dict[str, Any] | None = None,
        correlation_id: str | None = None,
    ) -> None:
        row = AuditLog(
            created_at=datetime.now(tz=UTC),
            action=action,
            actor_user_id=actor_user_id,
            tenant_id=tenant_id,
            context=context,
            correlation_id=correlation_id or get_correlation_id(),
        )
        self._db.add(row)
        self._db.commit()

    def list_for_tenant(
        self,
        tenant_id: UUID,
        *,
        limit: int,
        offset: int,
        since: datetime | None = None,
    ) -> list[AuditLog]:
        """Leitura só do tenant indicado (isolamento para UI admin / exportação SIEM)."""
        stmt = (
            select(AuditLog)
            .where(AuditLog.tenant_id == tenant_id)
            .order_by(AuditLog.created_at.desc(), AuditLog.id.desc())
        )
        if since is not None:
            stmt = stmt.where(AuditLog.created_at >= since)
        stmt = stmt.offset(offset).limit(limit)
        return list(self._db.scalars(stmt).all())

    def list_for_tenant_export(
        self,
        tenant_id: UUID,
        *,
        since: datetime | None = None,
        max_rows: int = 5000,
    ) -> list[AuditLog]:
        """Até `max_rows` eventos do tenant, ordenados por tempo crescente (adequado a CSV)."""
        stmt = (
            select(AuditLog)
            .where(AuditLog.tenant_id == tenant_id)
            .order_by(AuditLog.created_at.asc(), AuditLog.id.asc())
        )
        if since is not None:
            stmt = stmt.where(AuditLog.created_at >= since)
        stmt = stmt.limit(max_rows)
        return list(self._db.scalars(stmt).all())
