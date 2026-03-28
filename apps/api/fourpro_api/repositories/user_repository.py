from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from fourpro_api.models.user import User


class UserRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email.lower().strip())
        return self._db.scalars(stmt).first()

    def get_by_id(self, user_id: UUID) -> User | None:
        return self._db.get(User, user_id)

    def create(self, email: str, password_hash: str) -> User:
        from datetime import UTC, datetime

        now = datetime.now(tz=UTC)
        user = User(
            email=email.lower().strip(),
            password_hash=password_hash,
            is_active=True,
            mfa_enabled=False,
            created_at=now,
            updated_at=now,
        )
        self._db.add(user)
        self._db.commit()
        self._db.refresh(user)
        return user

    def update_password_hash(self, user: User, password_hash: str) -> None:
        from datetime import UTC, datetime

        user.password_hash = password_hash
        user.updated_at = datetime.now(tz=UTC)
        self._db.add(user)
        self._db.commit()
