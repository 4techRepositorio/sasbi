"""Validação de banco — rollback não persiste alterações."""

import uuid
from datetime import UTC, datetime

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from fourpro_api.models.user import User


@pytest.mark.integration
def test_session_rollback_discards_user(db_session: Session) -> None:
    now = datetime.now(tz=UTC)
    email = f"rollback-{uuid.uuid4().hex[:8]}@example.com"
    u = User(
        email=email,
        password_hash="x",
        is_active=True,
        mfa_enabled=False,
        created_at=now,
        updated_at=now,
    )
    db_session.add(u)
    db_session.flush()
    assert db_session.scalars(select(User).where(User.email == email)).first() is not None
    db_session.rollback()
    assert db_session.scalars(select(User).where(User.email == email)).first() is None
