"""add_dataset_eda

Revision ID: 006_dataset_eda
Revises: 005_dataset_cleanings
Create Date: 2026-08-01 13:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '006_dataset_eda'
down_revision: Union[str, None] = '005_dataset_cleanings'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'dataset_eda',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('dataset_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('datasets.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('summary', sa.Text(), nullable=False),
        sa.Column('statistics', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('correlations', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('outliers', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('charts', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('insights', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('report_path', sa.String(length=1024), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_dataset_eda_dataset_id', 'dataset_eda', ['dataset_id'])


def downgrade() -> None:
    op.drop_table('dataset_eda')
