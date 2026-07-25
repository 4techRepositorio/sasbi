"""Migração data_sources + connector_credentials + sync_runs (TICKET-015)

Revision ID: 0007_data_sources
Revises: 0006_core_storage_quotas
Create Date: 2026-07-25

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0007_data_sources"
down_revision: Union[str, Sequence[str], None] = "0006_core_storage_quotas"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "data_sources",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("connector_type", sa.String(length=64), nullable=False),
        sa.Column("config_json", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("last_sync_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column("created_by_user_id", sa.Uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_data_sources_tenant_id", "data_sources", ["tenant_id"])
    op.create_index("ix_data_sources_created_by_user_id", "data_sources", ["created_by_user_id"])

    op.create_table(
        "connector_credentials",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("data_source_id", sa.Uuid(), nullable=False),
        sa.Column("secret_encrypted", sa.Text(), nullable=False),
        sa.Column("key_version", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["data_source_id"], ["data_sources.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("data_source_id"),
    )
    op.create_index("ix_connector_credentials_tenant_id", "connector_credentials", ["tenant_id"])
    op.create_index(
        "ix_connector_credentials_data_source_id", "connector_credentials", ["data_source_id"]
    )

    op.create_table(
        "data_source_sync_runs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("data_source_id", sa.Uuid(), nullable=False),
        sa.Column("ingestion_id", sa.Uuid(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("object_id", sa.String(length=512), nullable=True),
        sa.Column("friendly_message", sa.Text(), nullable=True),
        sa.Column("technical_log", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["data_source_id"], ["data_sources.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["ingestion_id"], ["file_ingestions.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_data_source_sync_runs_tenant_id", "data_source_sync_runs", ["tenant_id"])
    op.create_index(
        "ix_data_source_sync_runs_data_source_id", "data_source_sync_runs", ["data_source_id"]
    )
    op.create_index(
        "ix_data_source_sync_runs_ingestion_id", "data_source_sync_runs", ["ingestion_id"]
    )


def downgrade() -> None:
    op.drop_index("ix_data_source_sync_runs_ingestion_id", table_name="data_source_sync_runs")
    op.drop_index("ix_data_source_sync_runs_data_source_id", table_name="data_source_sync_runs")
    op.drop_index("ix_data_source_sync_runs_tenant_id", table_name="data_source_sync_runs")
    op.drop_table("data_source_sync_runs")
    op.drop_index("ix_connector_credentials_data_source_id", table_name="connector_credentials")
    op.drop_index("ix_connector_credentials_tenant_id", table_name="connector_credentials")
    op.drop_table("connector_credentials")
    op.drop_index("ix_data_sources_created_by_user_id", table_name="data_sources")
    op.drop_index("ix_data_sources_tenant_id", table_name="data_sources")
    op.drop_table("data_sources")
