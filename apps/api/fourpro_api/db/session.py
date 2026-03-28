from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from fourpro_api.config import get_settings
from fourpro_api.db.base import Base

_engine = None
_session_maker = None


def reset_db_engine() -> None:
    """Limpa cache de engine (apenas testes)."""
    global _engine, _session_maker
    if _engine is not None:
        _engine.dispose()
    _engine = None
    _session_maker = None


def get_engine():
    global _engine
    if _engine is None:
        _engine = create_engine(get_settings().database_url, pool_pre_ping=True)
    return _engine


def get_session_maker():
    global _session_maker
    if _session_maker is None:
        _session_maker = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())
    return _session_maker


def get_db() -> Generator[Session, None, None]:
    db = get_session_maker()()
    try:
        yield db
    finally:
        db.close()


def init_db_schema() -> None:
    """Somente dev/testes sem Alembic — não usar em produção."""
    Base.metadata.create_all(bind=get_engine())
