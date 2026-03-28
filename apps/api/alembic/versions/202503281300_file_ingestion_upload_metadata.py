"""file_ingestion upload metadata sha256 uploaded_by

Revision ID: 0003_ingestion_meta
Revises: 0002_mvp
Create Date: 2025-03-28

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0003_ingestion_meta"
down_revision: Union[str, Sequence[str], None] = "0002_mvp"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("file_ingestions", sa.Column("uploaded_by_user_id", sa.Uuid(), nullable=True))
    op.add_column("file_ingestions", sa.Column("content_sha256", sa.String(length=64), nullable=True))
    op.create_foreign_key(
        "fk_file_ingestions_uploaded_by_user_id_users",
        "file_ingestions",
        "users",
        ["uploaded_by_user_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("fk_file_ingestions_uploaded_by_user_id_users", "file_ingestions", type_="foreignkey")
    op.drop_column("file_ingestions", "content_sha256")
    op.drop_column("file_ingestions", "uploaded_by_user_id")
