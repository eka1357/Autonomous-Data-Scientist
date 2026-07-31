"""add dataset status column

Revision ID: 002_add_dataset_status
Revises: 001_initial_schema
Create Date: 2026-07-31

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "002_add_dataset_status"
down_revision: Union[str, None] = "001_initial_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "datasets",
        sa.Column("status", sa.String(length=50), nullable=False, server_default="uploaded"),
    )


def downgrade() -> None:
    op.drop_column("datasets", "status")
