from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from fourpro_api.models.refresh_token import RefreshToken


class RefreshTokenRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def create(
        self,
        *,
        user_id: UUID,
        tenant_id: UUID | None,
        token_hash: str,
        expires_at: datetime,
    ) -> RefreshToken:
        now = datetime.now(tz=UTC)
        row = RefreshToken(
            user_id=user_id,
            tenant_id=tenant_id,
            token_hash=token_hash,
            expires_at=expires_at,
            revoked_at=None,
            created_at=now,
        )
        self._db.add(row)
        self._db.commit()
        self._db.refresh(row)
        return row

    def get_valid_by_hash(self, token_hash: str) -> RefreshToken | None:
        now = datetime.now(tz=UTC)
        stmt = select(RefreshToken).where(
            RefreshToken.token_hash == token_hash,
            RefreshToken.revoked_at.is_(None),
            RefreshToken.expires_at > now,
        )
        return self._db.scalars(stmt).first()

    def revoke(self, row: RefreshToken) -> None:
        row.revoked_at = datetime.now(tz=UTC)
        self._db.add(row)
        self._db.commit()

    def revoke_all_for_user(self, user_id: UUID) -> None:
        now = datetime.now(tz=UTC)
        self._db.execute(
            update(RefreshToken)
            .where(RefreshToken.user_id == user_id, RefreshToken.revoked_at.is_(None))
            .values(revoked_at=now),
        )
        self._db.commit()
