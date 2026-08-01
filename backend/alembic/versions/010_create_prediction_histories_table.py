"""create prediction_histories table

Revision ID: 010_prediction_history
Revises: 009_model_evaluation
Create Date: 2026-08-01 20:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "010_prediction_history"
down_revision: Union[str, None] = "009_model_evaluation"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "prediction_histories",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "dataset_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("datasets.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("prediction_type", sa.String(length=50), nullable=False),
        sa.Column("input_summary", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("output_summary", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("result_file_path", sa.String(length=1024), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="completed"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        op.f("ix_prediction_histories_dataset_id"),
        "prediction_histories",
        ["dataset_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_prediction_histories_user_id"),
        "prediction_histories",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_prediction_histories_user_id"), table_name="prediction_histories")
    op.drop_index(op.f("ix_prediction_histories_dataset_id"), table_name="prediction_histories")
    op.drop_table("prediction_histories")
