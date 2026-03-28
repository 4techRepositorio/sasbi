from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from fourpro_api.models.password_reset import PasswordResetToken


class PasswordResetRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def create(self, *, user_id: UUID, token_hash: str, expires_at: datetime) -> PasswordResetToken:
        now = datetime.now(tz=UTC)
        row = PasswordResetToken(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
            used_at=None,
            created_at=now,
        )
        self._db.add(row)
        self._db.commit()
        self._db.refresh(row)
        return row

    def get_valid_by_hash(self, token_hash: str) -> PasswordResetToken | None:
        now = datetime.now(tz=UTC)
        stmt = select(PasswordResetToken).where(
            PasswordResetToken.token_hash == token_hash,
            PasswordResetToken.used_at.is_(None),
            PasswordResetToken.expires_at > now,
        )
        return self._db.scalars(stmt).first()

    def mark_used(self, row: PasswordResetToken) -> None:
        row.used_at = datetime.now(tz=UTC)
        self._db.add(row)
        self._db.commit()
