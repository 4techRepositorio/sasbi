"""plans.max_data_sources for connector quotas

Revision ID: 0009_core_max_data_sources
Revises: 0008_data_semantic_dashboards
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0009_core_max_data_sources"
down_revision: Union[str, Sequence[str], None] = "0008_data_semantic_dashboards"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "plans",
        sa.Column("max_data_sources", sa.Integer(), nullable=False, server_default="10"),
    )
    op.execute("UPDATE plans SET max_data_sources = 25 WHERE code = 'pro'")
    op.execute("UPDATE plans SET max_data_sources = 10 WHERE code = 'starter'")
    op.alter_column("plans", "max_data_sources", server_default=None)


def downgrade() -> None:
    op.drop_column("plans", "max_data_sources")
