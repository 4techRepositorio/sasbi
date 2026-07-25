"""semantic_models dashboards dashboard_versions parsed_rows_json

Revision ID: 0008_data_semantic_dashboards
Revises: 0007_data_sources
Create Date: 2026-07-25

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0008_data_semantic_dashboards"
down_revision: Union[str, Sequence[str], None] = "0007_data_sources"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("file_ingestions", sa.Column("parsed_rows_json", sa.JSON(), nullable=True))

    op.create_table(
        "semantic_models",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("dataset_id", sa.Uuid(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("fields_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["dataset_id"], ["file_ingestions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_semantic_models_tenant_id"), "semantic_models", ["tenant_id"], unique=False)
    op.create_index(op.f("ix_semantic_models_dataset_id"), "semantic_models", ["dataset_id"], unique=False)
    op.create_index(
        "ix_semantic_models_tenant_id_name",
        "semantic_models",
        ["tenant_id", "name"],
        unique=False,
    )

    op.create_table(
        "dashboards",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="draft"),
        sa.Column("layout_json", sa.JSON(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_by_user_id", sa.Uuid(), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_dashboards_tenant_id"), "dashboards", ["tenant_id"], unique=False)
    op.create_index(
        op.f("ix_dashboards_created_by_user_id"),
        "dashboards",
        ["created_by_user_id"],
        unique=False,
    )
    op.create_index(
        "ix_dashboards_tenant_id_status",
        "dashboards",
        ["tenant_id", "status"],
        unique=False,
    )

    op.create_table(
        "dashboard_versions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("dashboard_id", sa.Uuid(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("layout_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["dashboard_id"], ["dashboards.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("dashboard_id", "version", name="uq_dashboard_versions_dashboard_version"),
    )
    op.create_index(
        op.f("ix_dashboard_versions_dashboard_id"),
        "dashboard_versions",
        ["dashboard_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_dashboard_versions_dashboard_id"), table_name="dashboard_versions")
    op.drop_table("dashboard_versions")
    op.drop_index("ix_dashboards_tenant_id_status", table_name="dashboards")
    op.drop_index(op.f("ix_dashboards_created_by_user_id"), table_name="dashboards")
    op.drop_index(op.f("ix_dashboards_tenant_id"), table_name="dashboards")
    op.drop_table("dashboards")
    op.drop_index("ix_semantic_models_tenant_id_name", table_name="semantic_models")
    op.drop_index(op.f("ix_semantic_models_dataset_id"), table_name="semantic_models")
    op.drop_index(op.f("ix_semantic_models_tenant_id"), table_name="semantic_models")
    op.drop_table("semantic_models")
    op.drop_column("file_ingestions", "parsed_rows_json")
