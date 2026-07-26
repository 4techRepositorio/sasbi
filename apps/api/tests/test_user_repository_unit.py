"""Unitários — UserRepository create/update."""

import pytest
from sqlalchemy.orm import Session

from fourpro_api.core.security import hash_password
from fourpro_api.repositories.user_repository import UserRepository


@pytest.mark.unit
@pytest.mark.auth
def test_user_repository_create_and_update_password(db_session: Session) -> None:
    repo = UserRepository(db_session)
    user = repo.create("New.User@Example.com", hash_password("initial-pass"))
    assert user.email == "new.user@example.com"
    assert user.is_active is True
    again = repo.get_by_email("new.user@example.com")
    assert again is not None
    assert again.id == user.id
    repo.update_password_hash(user, hash_password("rotated-pass"))
    db_session.refresh(user)
    assert user.password_hash
