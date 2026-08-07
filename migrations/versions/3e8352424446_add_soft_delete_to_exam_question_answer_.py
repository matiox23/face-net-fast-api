"""add soft delete to exam question answer_option

Revision ID: 3e8352424446
Revises: d37d57c953ff
Create Date: 2026-08-06 21:52:53.345023

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3e8352424446'
down_revision: Union[str, Sequence[str], None] = 'd37d57c953ff'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("ALTER TYPE academic.exam_status ADD VALUE IF NOT EXISTS 'deleted'")
    op.add_column(
        'answer_option',
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default=sa.false()),
        schema='academic',
    )
    op.add_column(
        'question',
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default=sa.false()),
        schema='academic',
    )
    op.alter_column('answer_option', 'is_deleted', server_default=None, schema='academic')
    op.alter_column('question', 'is_deleted', server_default=None, schema='academic')


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('question', 'is_deleted', schema='academic')
    op.drop_column('answer_option', 'is_deleted', schema='academic')
    # Postgres does not support removing enum values; DELETED stays in academic.exam_status.
