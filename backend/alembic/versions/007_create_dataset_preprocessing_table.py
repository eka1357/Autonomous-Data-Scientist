"""create dataset_preprocessings table

Revision ID: 007_dataset_preprocessing
Revises: 006_dataset_eda
Create Date: 2026-08-01 17:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "007_dataset_preprocessing"
down_revision: Union[str, None] = "006_dataset_eda"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "dataset_preprocessings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "dataset_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("datasets.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("target_column", sa.String(length=255), nullable=True),
        sa.Column("preprocessing_plan", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("execution_summary", postgresql.JSONB(), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="pending"),
        sa.Column("ml_ready_path", sa.String(length=1024), nullable=True),
        sa.Column("x_train_path", sa.String(length=1024), nullable=True),
        sa.Column("x_test_path", sa.String(length=1024), nullable=True),
        sa.Column("y_train_path", sa.String(length=1024), nullable=True),
        sa.Column("y_test_path", sa.String(length=1024), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        op.f("ix_dataset_preprocessings_dataset_id"),
        "dataset_preprocessings",
        ["dataset_id"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_dataset_preprocessings_dataset_id"), table_name="dataset_preprocessings")
    op.drop_table("dataset_preprocessings")
