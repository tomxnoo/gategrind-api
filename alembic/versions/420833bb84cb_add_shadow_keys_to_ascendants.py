"""add_shadow_keys_to_ascendants

Revision ID: 420833bb84cb
Revises: 1daf7f3cd988
Create Date: 2025-07-27 23:44:54.499838

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '420833bb84cb'
down_revision: Union[str, Sequence[str], None] = '1daf7f3cd988'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add shadow_keys column to ascendants table
    op.add_column('ascendants', sa.Column('shadow_keys', sa.Integer(), nullable=False, default=0))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove shadow_keys column from ascendants table
    op.drop_column('ascendants', 'shadow_keys')
