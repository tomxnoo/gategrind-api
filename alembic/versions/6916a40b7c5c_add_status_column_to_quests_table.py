"""Add status column to quests table

Revision ID: 6916a40b7c5c
Revises: 40a013621c94
Create Date: 2025-07-28 23:10:46.693446

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6916a40b7c5c'
down_revision: Union[str, Sequence[str], None] = '40a013621c94'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add status column to quests table
    op.add_column('quests', sa.Column('status', sa.String(20), nullable=False, server_default='active'))
    
    # Add index for status column
    op.create_index('idx_quests_status', 'quests', ['status'])
    
    # Add composite index for ascendant_id and status
    op.create_index('idx_quests_ascendant_status', 'quests', ['ascendant_id', 'status'])


def downgrade() -> None:
    """Downgrade schema."""
    # Drop indexes first
    op.drop_index('idx_quests_ascendant_status', 'quests')
    op.drop_index('idx_quests_status', 'quests')
    
    # Drop the status column
    op.drop_column('quests', 'status')
