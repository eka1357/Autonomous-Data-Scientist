"""create dataset_profiles table

Revision ID: 003_dataset_profiles
Revises: 002_add_dataset_status
Create Date: 2026-07-31

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as _sqla
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "003_dataset_profiles"
down_revision: Union[str, None] = "002_add_dataset_status"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "dataset_profiles",
        _sqla.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        _sqla.Column(
            "dataset_id",
            postgresql.UUID(as_uuid=True),
            _sqla.ForeignKey("datasets.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        _sqla.Column("column_names", postgresql.JSONB(), nullable=False),
        _sqla.Column("data_types", postgresql.JSONB(), nullable=False),
        _sqla.Column("missing_values", postgresql.JSONB(), nullable=False),
        _sqla.Column("duplicate_row_count", _sqla.BigInteger(), nullable=False, server_default="0"),
        _sqla.Column("summary_stats", postgresql.JSONB(), nullable=False),
        _sqla.Column("created_at", _sqla.DateTime(timezone=True), nullable=False),
        _sqla.Column("updated_at", _sqla.DateTime(timezone=True), nullable=False),
    )
    op.create_index(op.f("ix_dataset_profiles_dataset_id"), "dataset_profiles", ["dataset_id"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_dataset_profiles_dataset_id"), table_name="dataset_profiles")
    op.drop_table("dataset_profiles")
