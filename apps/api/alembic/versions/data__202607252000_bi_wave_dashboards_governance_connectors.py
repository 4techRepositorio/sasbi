"""BI wave: layers, dashboards, connectors, semantic, correlation

Revision ID: 0007_data_bi_wave
Revises: 0006_core_storage_quotas
Create Date: 2026-07-25

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0007_data_bi_wave"
down_revision: Union[str, Sequence[str], None] = "0006_core_storage_quotas"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "file_ingestions",
        sa.Column("layer", sa.String(length=16), nullable=False, server_default="bronze"),
    )
    op.add_column(
        "file_ingestions",
        sa.Column("source_ingestion_id", sa.Uuid(), nullable=True),
    )
    op.add_column(
        "file_ingestions",
        sa.Column("transform_version", sa.String(length=64), nullable=True),
    )
    op.add_column(
        "file_ingestions",
        sa.Column("correlation_id", sa.String(length=64), nullable=True),
    )
    op.create_index("ix_file_ingestions_source_ingestion_id", "file_ingestions", ["source_ingestion_id"])
    op.create_index("ix_file_ingestions_correlation_id", "file_ingestions", ["correlation_id"])
    op.create_foreign_key(
        "fk_file_ingestions_source_ingestion_id",
        "file_ingestions",
        "file_ingestions",
        ["source_ingestion_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.add_column("audit_log", sa.Column("correlation_id", sa.String(length=64), nullable=True))
    op.create_index("ix_audit_log_correlation_id", "audit_log", ["correlation_id"])

    op.create_table(
        "dashboards",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("layout_json", sa.JSON(), nullable=False),
        sa.Column("created_by_user_id", sa.Uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_dashboards_tenant_id", "dashboards", ["tenant_id"])

    op.create_table(
        "dashboard_widgets",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("dashboard_id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("widget_type", sa.String(length=32), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("dataset_id", sa.Uuid(), nullable=True),
        sa.Column("config", sa.JSON(), nullable=False),
        sa.Column("position", sa.JSON(), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["dashboard_id"], ["dashboards.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["dataset_id"], ["file_ingestions.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_dashboard_widgets_dashboard_id", "dashboard_widgets", ["dashboard_id"])
    op.create_index("ix_dashboard_widgets_tenant_id", "dashboard_widgets", ["tenant_id"])

    op.create_table(
        "data_sources",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("connector_type", sa.String(length=64), nullable=False),
        sa.Column("config_json", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_by_user_id", sa.Uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_data_sources_tenant_id", "data_sources", ["tenant_id"])

    op.create_table(
        "connector_credentials",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("data_source_id", sa.Uuid(), nullable=False),
        sa.Column("secret_encrypted", sa.LargeBinary(), nullable=False),
        sa.Column("key_version", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["data_source_id"], ["data_sources.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("data_source_id"),
    )
    op.create_index("ix_connector_credentials_tenant_id", "connector_credentials", ["tenant_id"])

    op.create_table(
        "data_source_sync_runs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("data_source_id", sa.Uuid(), nullable=False),
        sa.Column("ingestion_id", sa.Uuid(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("correlation_id", sa.String(length=64), nullable=True),
        sa.Column("friendly_error", sa.Text(), nullable=True),
        sa.Column("technical_log", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
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
        "ix_data_source_sync_runs_correlation_id", "data_source_sync_runs", ["correlation_id"]
    )

    op.create_table(
        "semantic_models",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("dataset_id", sa.Uuid(), nullable=False),
        sa.Column("dimensions_json", sa.JSON(), nullable=False),
        sa.Column("measures_json", sa.JSON(), nullable=False),
        sa.Column("created_by_user_id", sa.Uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["dataset_id"], ["file_ingestions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_semantic_models_tenant_id", "semantic_models", ["tenant_id"])
    op.create_index("ix_semantic_models_dataset_id", "semantic_models", ["dataset_id"])


def downgrade() -> None:
    op.drop_table("semantic_models")
    op.drop_table("data_source_sync_runs")
    op.drop_table("connector_credentials")
    op.drop_table("data_sources")
    op.drop_table("dashboard_widgets")
    op.drop_table("dashboards")
    op.drop_index("ix_audit_log_correlation_id", table_name="audit_log")
    op.drop_column("audit_log", "correlation_id")
    op.drop_constraint("fk_file_ingestions_source_ingestion_id", "file_ingestions", type_="foreignkey")
    op.drop_index("ix_file_ingestions_correlation_id", table_name="file_ingestions")
    op.drop_index("ix_file_ingestions_source_ingestion_id", table_name="file_ingestions")
    op.drop_column("file_ingestions", "correlation_id")
    op.drop_column("file_ingestions", "transform_version")
    op.drop_column("file_ingestions", "source_ingestion_id")
    op.drop_column("file_ingestions", "layer")
