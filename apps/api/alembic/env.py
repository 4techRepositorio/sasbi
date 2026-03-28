from alembic import context
from sqlalchemy import engine_from_config, pool

from fourpro_api.config import get_settings
from fourpro_api.db.base import Base
from fourpro_api.models import (  # noqa: F401
    AuditLog,
    FileIngestion,
    MfaPendingChallenge,
    PasswordResetToken,
    Plan,
    RefreshToken,
    Tenant,
    TenantMembership,
    TenantQuotaGroup,
    TenantSubscription,
    User,
)

config = context.config

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = get_settings().database_url
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section) or {}
    configuration["sqlalchemy.url"] = get_settings().database_url
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
