"""create dataset_cleanings table

Revision ID: 005_dataset_cleanings
Revises: 004_dataset_analysis
Create Date: 2026-07-31

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as _sqla
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "005_dataset_cleanings"
down_revision: Union[str, None] = "004_dataset_analysis"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "dataset_cleanings",
        _sqla.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        _sqla.Column(
            "dataset_id",
            postgresql.UUID(as_uuid=True),
            _sqla.ForeignKey("datasets.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        _sqla.Column("cleaning_plan", postgresql.JSONB(), nullable=False),
        _sqla.Column("execution_summary", postgresql.JSONB(), nullable=True),
        _sqla.Column("status", _sqla.String(length=50), nullable=False, server_default="pending"),
        _sqla.Column("created_at", _sqla.DateTime(timezone=True), nullable=False),
        _sqla.Column("updated_at", _sqla.DateTime(timezone=True), nullable=False),
    )
    op.create_index(op.f("ix_dataset_cleanings_dataset_id"), "dataset_cleanings", ["dataset_id"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_dataset_cleanings_dataset_id"), table_name="dataset_cleanings")
    op.drop_table("dataset_cleanings")
