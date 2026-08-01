"""create model_trainings table

Revision ID: 008_model_training
Revises: 007_dataset_preprocessing
Create Date: 2026-08-01 18:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "008_model_training"
down_revision: Union[str, None] = "007_dataset_preprocessing"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "model_trainings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "dataset_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("datasets.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("problem_type", sa.String(length=50), nullable=False),
        sa.Column("target_column", sa.String(length=255), nullable=True),
        sa.Column("best_algorithm", sa.String(length=100), nullable=True),
        sa.Column("best_score", sa.Float(), nullable=True),
        sa.Column("primary_metric", sa.String(length=50), nullable=True),
        sa.Column("leaderboard", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("model_path", sa.String(length=1024), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        op.f("ix_model_trainings_dataset_id"),
        "model_trainings",
        ["dataset_id"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_model_trainings_dataset_id"), table_name="model_trainings")
    op.drop_table("model_trainings")
