"""
Fix Awakening System Database Schema

This migration fixes the schema mismatch between the migration and SQLAlchemy models.
It updates the awakening_sessions table to match the model definition exactly.
"""

from alembic import op
import sqlalchemy as sa
from datetime import datetime


def upgrade():
    """Fix awakening system schema to match models"""
    
    # Drop the existing awakening_sessions table and recreate with correct schema
    op.drop_table('awakening_sessions')
    
    # Create awakening_sessions table with correct schema matching the model
    op.create_table(
        'awakening_sessions',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('user_id', sa.Integer(), nullable=False, index=True),
        sa.Column('session_date', sa.Date(), nullable=False, index=True),
        sa.Column('tier_level', sa.String(20), nullable=False, default="normal"),
        sa.Column('status', sa.String(20), nullable=False, default="active", index=True),
        sa.Column('reset_used', sa.Boolean(), nullable=False, default=False),
        sa.Column('reset_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=datetime.utcnow),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Update awakening_rewards table to match the model
    op.drop_table('awakening_rewards')
    
    op.create_table(
        'awakening_rewards',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('session_id', sa.Integer(), nullable=False, index=True),
        sa.Column('shadow_keys', sa.Integer(), nullable=False, default=0),
        sa.Column('xp_gained', sa.Integer(), nullable=False, default=0),
        sa.Column('stat_points', sa.Integer(), nullable=False, default=0),
        sa.Column('aura_change', sa.Integer(), nullable=False, default=0),
        sa.Column('streak_bonus', sa.Integer(), nullable=False, default=0),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=datetime.utcnow),
        sa.ForeignKeyConstraint(['session_id'], ['awakening_sessions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Update user_awakening_progress table to match the model
    op.drop_table('user_awakening_progress')
    
    op.create_table(
        'user_awakening_progress',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('user_id', sa.Integer(), nullable=False, index=True),
        sa.Column('quest_id', sa.Integer(), nullable=False, index=True),
        sa.Column('progress_reps', sa.Integer(), nullable=False, default=0),
        sa.Column('progress_time', sa.Integer(), nullable=False, default=0),
        sa.Column('progress_distance', sa.Integer(), nullable=False, default=0),
        sa.Column('last_updated', sa.DateTime(), nullable=False, default=datetime.utcnow),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('rewards_claimed', sa.Boolean(), nullable=False, default=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['quest_id'], ['awakening_quests.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Recreate indexes to match the model definitions
    
    # Awakening Sessions indexes
    op.create_index('idx_awakening_sessions_user_date', 'awakening_sessions', ['user_id', 'session_date'])
    op.create_index('idx_awakening_sessions_status', 'awakening_sessions', ['status'])
    
    # Awakening Quests indexes (these should already exist from original migration)
    # But let's ensure they match the model
    op.create_index('idx_awakening_quests_session', 'awakening_quests', ['session_id'], if_not_exists=True)
    op.create_index('idx_awakening_quests_type_status', 'awakening_quests', ['quest_type', 'status'], if_not_exists=True)
    op.create_index('idx_awakening_quests_movement', 'awakening_quests', ['target_movement_id'], if_not_exists=True)
    
    # Awakening Rewards indexes
    op.create_index('idx_awakening_rewards_session', 'awakening_rewards', ['session_id'])
    
    # User Awakening Progress indexes
    op.create_index('idx_user_awakening_progress_user_quest', 'user_awakening_progress', ['user_id', 'quest_id'])
    op.create_index('idx_user_awakening_progress_completed', 'user_awakening_progress', ['completed_at'])


def downgrade():
    """Revert to original schema"""
    
    # Drop the fixed tables
    op.drop_table('user_awakening_progress')
    op.drop_table('awakening_rewards')
    op.drop_table('awakening_sessions')
    
    # Recreate original awakening_sessions table
    op.create_table(
        'awakening_sessions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('readiness_level', sa.Integer(), nullable=False),
        sa.Column('quest_count', sa.Integer(), nullable=False, default=3),
        sa.Column('completed_quests', sa.Integer(), nullable=False, default=0),
        sa.Column('is_completed', sa.Boolean(), nullable=False, default=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=datetime.utcnow),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Recreate original awakening_rewards table
    op.create_table(
        'awakening_rewards',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('session_id', sa.Integer(), nullable=False),
        sa.Column('quest_id', sa.Integer(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('reward_type', sa.String(50), nullable=False),
        sa.Column('amount', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=datetime.utcnow),
        sa.Column('applied_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['session_id'], ['awakening_sessions.id'], ),
        sa.ForeignKeyConstraint(['quest_id'], ['awakening_quests.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Recreate original user_awakening_progress table
    op.create_table(
        'user_awakening_progress',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('current_streak', sa.Integer(), nullable=False, default=0),
        sa.Column('longest_streak', sa.Integer(), nullable=False, default=0),
        sa.Column('last_session_date', sa.DateTime(), nullable=True),
        sa.Column('total_sessions_completed', sa.Integer(), nullable=False, default=0),
        sa.Column('total_quests_completed', sa.Integer(), nullable=False, default=0),
        sa.Column('total_xp_earned', sa.Integer(), nullable=False, default=0),
        sa.Column('total_aura_earned', sa.Integer(), nullable=False, default=0),
        sa.Column('total_shadow_keys_earned', sa.Integer(), nullable=False, default=0),
        sa.Column('average_readiness_level', sa.Integer(), nullable=True),
        sa.Column('preferred_difficulty', sa.String(20), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime(), nullable=False, default=datetime.utcnow),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    
    # Recreate original indexes
    op.create_index('idx_awakening_sessions_user_date', 'awakening_sessions', ['user_id', 'created_at'])
    op.create_index('idx_awakening_sessions_user_completed', 'awakening_sessions', ['user_id', 'is_completed'])
    op.create_index('idx_awakening_sessions_created_at', 'awakening_sessions', ['created_at'])
    op.create_index('idx_awakening_sessions_readiness', 'awakening_sessions', ['readiness_level'])