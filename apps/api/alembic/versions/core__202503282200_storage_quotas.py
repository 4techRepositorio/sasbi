"""tenant quota groups + per-user storage cap on membership

Revision ID: 0006_core_storage_quotas
Revises: 0005_data_tenant_status_idx
Create Date: 2026-03-28

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0006_core_storage_quotas"
down_revision: Union[str, Sequence[str], None] = "0005_data_tenant_status_idx"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "tenant_quota_groups",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("max_storage_mb", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_tenant_quota_groups_tenant_id"), "tenant_quota_groups", ["tenant_id"], unique=False)

    op.add_column("tenant_memberships", sa.Column("max_storage_mb", sa.Integer(), nullable=True))
    op.add_column("tenant_memberships", sa.Column("quota_group_id", sa.Uuid(), nullable=True))
    op.create_index(
        op.f("ix_tenant_memberships_quota_group_id"),
        "tenant_memberships",
        ["quota_group_id"],
        unique=False,
    )
    op.create_foreign_key(
        "fk_tenant_memberships_quota_group_id",
        "tenant_memberships",
        "tenant_quota_groups",
        ["quota_group_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("fk_tenant_memberships_quota_group_id", "tenant_memberships", type_="foreignkey")
    op.drop_index(op.f("ix_tenant_memberships_quota_group_id"), table_name="tenant_memberships")
    op.drop_column("tenant_memberships", "quota_group_id")
    op.drop_column("tenant_memberships", "max_storage_mb")
    op.drop_index(op.f("ix_tenant_quota_groups_tenant_id"), table_name="tenant_quota_groups")
    op.drop_table("tenant_quota_groups")
