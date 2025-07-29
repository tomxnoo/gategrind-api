"""Fix dungeon columns

Revision ID: fix_dungeon_columns
Revises: 535ff58ce337
Create Date: 2025-01-28 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fix_dungeon_columns'
down_revision = '535ff58ce337'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add missing columns to dungeon_progress
    op.add_column('dungeon_progress', sa.Column('total_completions', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('dungeon_progress', sa.Column('total_shadow_keys_spent', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('dungeon_progress', sa.Column('total_shadow_essence_earned', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('dungeon_progress', sa.Column('last_completion_date', sa.DateTime(timezone=True), nullable=True))
    op.add_column('dungeon_progress', sa.Column('best_completion_time', sa.Integer(), nullable=True))
    
    # Add missing columns to dungeon_sessions
    op.add_column('dungeon_sessions', sa.Column('shadow_keys_spent', sa.Integer(), nullable=False, server_default='1'))
    op.add_column('dungeon_sessions', sa.Column('session_status', sa.String(length=20), nullable=False, server_default='active'))
    op.add_column('dungeon_sessions', sa.Column('trial_data', sa.JSON(), nullable=True))
    op.add_column('dungeon_sessions', sa.Column('daily_modifier_id', sa.BigInteger(), nullable=True))
    
    # Add foreign key for daily_modifier_id
    op.create_foreign_key(None, 'dungeon_sessions', 'daily_modifiers', ['daily_modifier_id'], ['id'])


def downgrade() -> None:
    # Remove foreign key
    op.drop_constraint(None, 'dungeon_sessions', type_='foreignkey')
    
    # Remove columns from dungeon_sessions
    op.drop_column('dungeon_sessions', 'daily_modifier_id')
    op.drop_column('dungeon_sessions', 'trial_data')
    op.drop_column('dungeon_sessions', 'session_status')
    op.drop_column('dungeon_sessions', 'shadow_keys_spent')
    
    # Remove columns from dungeon_progress
    op.drop_column('dungeon_progress', 'best_completion_time')
    op.drop_column('dungeon_progress', 'last_completion_date')
    op.drop_column('dungeon_progress', 'total_shadow_essence_earned')
    op.drop_column('dungeon_progress', 'total_shadow_keys_spent')
    op.drop_column('dungeon_progress', 'total_completions')