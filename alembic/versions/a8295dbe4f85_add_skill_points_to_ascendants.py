"""add_skill_points_to_ascendants

Revision ID: a8295dbe4f85
Revises: 313123a105ed
Create Date: 2025-07-25 02:23:05.702915

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a8295dbe4f85'
down_revision: Union[str, Sequence[str], None] = '313123a105ed'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add skill_points column to ascendants table for Shadow Essence
    op.add_column('ascendants', sa.Column('skill_points', sa.Integer(), nullable=False, server_default='0'))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove skill_points column from ascendants table
    op.drop_column('ascendants', 'skill_points')
