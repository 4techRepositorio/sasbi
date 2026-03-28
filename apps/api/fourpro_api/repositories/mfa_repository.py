from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.orm import Session

from fourpro_api.models.mfa import MfaPendingChallenge


class MfaRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def upsert_challenge(self, user_id: UUID, code_hash: str, expires_at: datetime) -> None:
        row = self._db.get(MfaPendingChallenge, user_id)
        if row is None:
            row = MfaPendingChallenge(user_id=user_id, code_hash=code_hash, expires_at=expires_at)
            self._db.add(row)
        else:
            row.code_hash = code_hash
            row.expires_at = expires_at
            self._db.add(row)
        self._db.commit()

    def get_valid(self, user_id: UUID) -> MfaPendingChallenge | None:
        row = self._db.get(MfaPendingChallenge, user_id)
        if row is None:
            return None
        exp = row.expires_at
        if exp.tzinfo is None:
            exp = exp.replace(tzinfo=UTC)
        if exp <= datetime.now(tz=UTC):
            return None
        return row

    def delete(self, user_id: UUID) -> None:
        row = self._db.get(MfaPendingChallenge, user_id)
        if row:
            self._db.delete(row)
            self._db.commit()
