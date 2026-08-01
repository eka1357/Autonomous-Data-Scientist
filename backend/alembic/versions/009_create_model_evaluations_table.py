"""create model_evaluations table

Revision ID: 009_model_evaluation
Revises: 008_model_training
Create Date: 2026-08-01 19:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "009_model_evaluation"
down_revision: Union[str, None] = "008_model_training"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "model_evaluations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "dataset_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("datasets.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("metrics", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("feature_importance", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("shap_values", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("report_path", sa.String(length=1024), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        op.f("ix_model_evaluations_dataset_id"),
        "model_evaluations",
        ["dataset_id"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_model_evaluations_dataset_id"), table_name="model_evaluations")
    op.drop_table("model_evaluations")
