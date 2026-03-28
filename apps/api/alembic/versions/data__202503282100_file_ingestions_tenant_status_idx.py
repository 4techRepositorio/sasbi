"""índice file_ingestions (tenant_id, status) para catálogo e listagens

Revision ID: 0005_data_tenant_status_idx
Revises: 0004_audit_log
Create Date: 2026-03-28

"""

from typing import Sequence, Union

from alembic import op

revision: str = "0005_data_tenant_status_idx"
down_revision: Union[str, Sequence[str], None] = "0004_audit_log"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index(
        "ix_file_ingestions_tenant_id_status",
        "file_ingestions",
        ["tenant_id", "status"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_file_ingestions_tenant_id_status", table_name="file_ingestions")
