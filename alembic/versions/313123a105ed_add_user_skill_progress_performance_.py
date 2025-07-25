"""add_user_skill_progress_performance_indexes

Revision ID: 313123a105ed
Revises: e8cd40744a50
Create Date: 2025-07-25 01:55:42.097023

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '313123a105ed'
down_revision: Union[str, Sequence[str], None] = 'e8cd40744a50'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add performance indexes for UserSkillProgress table."""
    # Performance indexes for common queries
    op.create_index('idx_user_skill_progress_ascendant_id', 'user_skill_progress', ['ascendant_id'])
    op.create_index('idx_user_skill_progress_node_id', 'user_skill_progress', ['node_id'])
    op.create_index('idx_user_skill_progress_unlocked_at', 'user_skill_progress', ['unlocked_at'])
    
    # Composite index for common queries (user's progress in specific categories)
    op.create_index('idx_user_skill_progress_ascendant_unlocked', 'user_skill_progress', ['ascendant_id', 'unlocked_at'])


def downgrade() -> None:
    """Remove performance indexes for UserSkillProgress table."""
    # Drop indexes in reverse order
    op.drop_index('idx_user_skill_progress_ascendant_unlocked', table_name='user_skill_progress')
    op.drop_index('idx_user_skill_progress_unlocked_at', table_name='user_skill_progress')
    op.drop_index('idx_user_skill_progress_node_id', table_name='user_skill_progress')
    op.drop_index('idx_user_skill_progress_ascendant_id', table_name='user_skill_progress')
