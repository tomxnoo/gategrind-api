"""create_dungeon_system_tables

Revision ID: 1daf7f3cd988
Revises: 1731f4e90808
Create Date: 2025-07-27 16:27:58.120657

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from datetime import datetime


# revision identifiers, used by Alembic.
revision: str = '1daf7f3cd988'
down_revision: Union[str, Sequence[str], None] = '1731f4e90808'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create dungeon system tables and indexes."""
    
    # Create daily_modifiers table first (no dependencies)
    op.create_table(
        'daily_modifiers',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('date', sa.Date(), nullable=False, unique=True),
        sa.Column('modifier_type', sa.String(30), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('stat_bonus', sa.String(20), nullable=True),
        sa.Column('difficulty_multiplier', sa.Numeric(3, 2), default=1.0),
        sa.Column('reward_multiplier', sa.Numeric(3, 2), default=1.0),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint("modifier_type IN ('strength_focus', 'endurance_boost', 'speed_challenge', 'precision_test', 'power_surge')", name='check_modifier_type')
    )
    
    # Create dungeon_sessions table - supports infinite levels
    op.create_table(
        'dungeon_sessions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('ascendant_id', sa.Integer(), nullable=False),
        sa.Column('dungeon_level', sa.Integer(), nullable=False),
        sa.Column('shadow_keys_spent', sa.Integer(), nullable=False, default=1),  # Always 1
        sa.Column('session_status', sa.String(20), default='active', nullable=False),
        sa.Column('trial_data', sa.JSON(), nullable=True),
        sa.Column('daily_modifier_id', sa.Integer(), nullable=True),
        sa.Column('current_trial_id', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True, nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['ascendant_id'], ['ascendants.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['daily_modifier_id'], ['daily_modifiers.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint("dungeon_level > 0", name='check_dungeon_level_positive'),  # No upper limit for infinite progression
        sa.CheckConstraint("session_status IN ('active', 'completed', 'failed', 'abandoned')", name='check_session_status')
    )
    
    # Create dungeon_trials table
    op.create_table(
        'dungeon_trials',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('session_id', sa.Integer(), nullable=False),
        sa.Column('trial_number', sa.Integer(), nullable=False),
        sa.Column('trial_type', sa.String(50), nullable=False),
        sa.Column('movement_id', sa.Integer(), nullable=True),
        sa.Column('required_reps', sa.Integer(), nullable=False),
        sa.Column('completed_reps', sa.Integer(), default=0, nullable=False),
        sa.Column('trial_status', sa.String(20), default='pending', nullable=False),
        sa.Column('is_completed', sa.Boolean(), default=False, nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('trial_data', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['session_id'], ['dungeon_sessions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['movement_id'], ['movements.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint("trial_number > 0", name='check_trial_number_positive'),
        sa.CheckConstraint("required_reps > 0", name='check_required_reps_positive'),
        sa.CheckConstraint("completed_reps >= 0", name='check_completed_reps_non_negative'),
        sa.CheckConstraint("trial_status IN ('pending', 'active', 'completed', 'failed')", name='check_trial_status')
    )
    
    # Create dungeon_rewards table
    op.create_table(
        'dungeon_rewards',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('session_id', sa.Integer(), nullable=False),
        sa.Column('ascendant_id', sa.Integer(), nullable=False),
        sa.Column('reward_type', sa.String(50), nullable=False),
        sa.Column('reward_amount', sa.Integer(), nullable=False),
        sa.Column('is_claimed', sa.Boolean(), default=False, nullable=False),
        sa.Column('earned_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('claimed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('reward_data', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['session_id'], ['dungeon_sessions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['ascendant_id'], ['ascendants.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint("reward_amount > 0", name='check_reward_amount_positive'),
        sa.CheckConstraint("reward_type IN ('aura', 'shadow_essence', 'stat_points', 'xp_bonus')", name='check_reward_type')
    )
    
    # Create dungeon_level_unlocks table
    op.create_table(
        'dungeon_level_unlocks',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('ascendant_id', sa.Integer(), nullable=False),
        sa.Column('dungeon_level', sa.Integer(), nullable=False),
        sa.Column('unlocked_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('unlock_requirements', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['ascendant_id'], ['ascendants.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('ascendant_id', 'dungeon_level', name='uq_ascendant_dungeon_level'),
        sa.CheckConstraint("dungeon_level > 0", name='check_unlock_level_positive')
    )
    
    # Add foreign key constraint for current_trial_id after dungeon_trials table is created
    op.create_foreign_key(
        'fk_dungeon_sessions_current_trial',
        'dungeon_sessions', 'dungeon_trials',
        ['current_trial_id'], ['id'],
        ondelete='SET NULL'
    )
    
    # Create all indexes
    create_indexes()


def create_indexes():
    """Create performance indexes."""
    # Daily Modifiers indexes
    op.create_index('idx_daily_modifiers_date', 'daily_modifiers', ['date'], unique=True)
    op.create_index('idx_daily_modifiers_type', 'daily_modifiers', ['modifier_type'])
    
    # Dungeon Sessions indexes
    op.create_index('idx_dungeon_sessions_ascendant', 'dungeon_sessions', ['ascendant_id'])
    op.create_index('idx_dungeon_sessions_level', 'dungeon_sessions', ['dungeon_level'])
    op.create_index('idx_dungeon_sessions_status', 'dungeon_sessions', ['session_status'])
    op.create_index('idx_dungeon_sessions_active', 'dungeon_sessions', ['is_active'])
    op.create_index('idx_dungeon_sessions_started', 'dungeon_sessions', ['started_at'])
    op.create_index('idx_dungeon_sessions_ascendant_level', 'dungeon_sessions', ['ascendant_id', 'dungeon_level'])
    op.create_index('idx_dungeon_sessions_expires_at', 'dungeon_sessions', ['expires_at'])
    
    # Dungeon Trials indexes
    op.create_index('idx_dungeon_trials_session', 'dungeon_trials', ['session_id'])
    op.create_index('idx_dungeon_trials_number', 'dungeon_trials', ['trial_number'])
    op.create_index('idx_dungeon_trials_type', 'dungeon_trials', ['trial_type'])
    op.create_index('idx_dungeon_trials_status', 'dungeon_trials', ['trial_status'])
    op.create_index('idx_dungeon_trials_completed', 'dungeon_trials', ['is_completed'])
    op.create_index('idx_dungeon_trials_started', 'dungeon_trials', ['started_at'])
    
    # Dungeon Rewards indexes
    op.create_index('idx_dungeon_rewards_session', 'dungeon_rewards', ['session_id'])
    op.create_index('idx_dungeon_rewards_ascendant', 'dungeon_rewards', ['ascendant_id'])
    op.create_index('idx_dungeon_rewards_type', 'dungeon_rewards', ['reward_type'])
    op.create_index('idx_dungeon_rewards_claimed', 'dungeon_rewards', ['is_claimed'])
    op.create_index('idx_dungeon_rewards_earned', 'dungeon_rewards', ['earned_at'])
    
    # Dungeon Level Unlocks indexes
    op.create_index('idx_dungeon_level_unlocks_ascendant', 'dungeon_level_unlocks', ['ascendant_id'])
    op.create_index('idx_dungeon_level_unlocks_level', 'dungeon_level_unlocks', ['dungeon_level'])


def downgrade() -> None:
    """Drop dungeon system tables and indexes."""
    # Drop foreign key constraint first
    op.drop_constraint('fk_dungeon_sessions_current_trial', 'dungeon_sessions', type_='foreignkey')
    
    # Drop in reverse order due to foreign key constraints
    op.drop_table('dungeon_level_unlocks')
    op.drop_table('dungeon_rewards')
    op.drop_table('dungeon_trials')
    op.drop_table('dungeon_sessions')
    op.drop_table('daily_modifiers')
