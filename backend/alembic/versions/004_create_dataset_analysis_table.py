"""create dataset_analysis table

Revision ID: 004_dataset_analysis
Revises: 003_dataset_profiles
Create Date: 2026-07-31

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as _sqla
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "004_dataset_analysis"
down_revision: Union[str, None] = "003_dataset_profiles"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "dataset_analysis",
        _sqla.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        _sqla.Column(
            "dataset_id",
            postgresql.UUID(as_uuid=True),
            _sqla.ForeignKey("datasets.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        _sqla.Column("summary", _sqla.Text(), nullable=False),
        _sqla.Column("quality_assessment", postgresql.JSONB(), nullable=False),
        _sqla.Column("recommended_ml_task", _sqla.String(length=50), nullable=True),
        _sqla.Column("target_column_candidate", _sqla.String(length=255), nullable=True),
        _sqla.Column("insights", postgresql.JSONB(), nullable=False),
        _sqla.Column("raw_llm_response", postgresql.JSONB(), nullable=True),
        _sqla.Column("created_at", _sqla.DateTime(timezone=True), nullable=False),
        _sqla.Column("updated_at", _sqla.DateTime(timezone=True), nullable=False),
    )
    op.create_index(op.f("ix_dataset_analysis_dataset_id"), "dataset_analysis", ["dataset_id"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_dataset_analysis_dataset_id"), table_name="dataset_analysis")
    op.drop_table("dataset_analysis")
