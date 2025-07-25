"""
Database Migration for Awakening System

This migration creates the necessary tables and indexes for the awakening system.
Run this after implementing the awakening models.
"""

from alembic import op
import sqlalchemy as sa
from datetime import datetime


def upgrade():
    """Create awakening system tables and indexes"""
    
    # Create awakening_sessions table
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
    
    # Create awakening_quests table
    op.create_table('awakening_quests',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.Integer(), nullable=False),
        sa.Column('quest_type', sa.String(length=50), nullable=False),
        sa.Column('target_movement_id', sa.Integer(), nullable=True),
        sa.Column('target_movement', sa.String(length=100), nullable=True),
        sa.Column('target_reps', sa.Integer(), nullable=True),
        sa.Column('target_time', sa.Integer(), nullable=True),
        sa.Column('target_distance', sa.Integer(), nullable=True),
        sa.Column('difficulty_level', sa.String(length=20), nullable=False, default='moderate'),
        sa.Column('parameters', sa.JSON(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, default='active'),
        sa.Column('progress_reps', sa.Integer(), nullable=False, default=0),
        sa.Column('progress_time', sa.Integer(), nullable=False, default=0),
        sa.Column('progress_distance', sa.Integer(), nullable=False, default=0),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=sa.func.now()),
        sa.ForeignKeyConstraint(['session_id'], ['awakening_sessions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create awakening_rewards table
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
    
    # Create user_awakening_progress table
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
    
    # Create indexes for performance optimization
    
    # Awakening Sessions indexes
    op.create_index('idx_awakening_sessions_user_date', 'awakening_sessions', ['user_id', 'created_at'])
    op.create_index('idx_awakening_sessions_user_completed', 'awakening_sessions', ['user_id', 'is_completed'])
    op.create_index('idx_awakening_sessions_created_at', 'awakening_sessions', ['created_at'])
    op.create_index('idx_awakening_sessions_readiness', 'awakening_sessions', ['readiness_level'])
    
    # Awakening Quests indexes
    op.create_index('idx_awakening_quests_session', 'awakening_quests', ['session_id'])
    op.create_index('idx_awakening_quests_movement', 'awakening_quests', ['target_movement_id'])
    op.create_index('idx_awakening_quests_completed', 'awakening_quests', ['status'])
    op.create_index('idx_awakening_quests_difficulty', 'awakening_quests', ['difficulty_level'])
    op.create_index('idx_awakening_quests_type', 'awakening_quests', ['quest_type'])
    
    # Awakening Rewards indexes
    op.create_index('idx_awakening_rewards_session', 'awakening_rewards', ['session_id'])
    op.create_index('idx_awakening_rewards_user', 'awakening_rewards', ['user_id'])
    op.create_index('idx_awakening_rewards_quest', 'awakening_rewards', ['quest_id'])
    op.create_index('idx_awakening_rewards_type', 'awakening_rewards', ['reward_type'])
    op.create_index('idx_awakening_rewards_created', 'awakening_rewards', ['created_at'])
    
    # User Awakening Progress indexes
    op.create_index('idx_user_awakening_progress_user', 'user_awakening_progress', ['user_id'])
    op.create_index('idx_user_awakening_progress_streak', 'user_awakening_progress', ['current_streak'])
    op.create_index('idx_user_awakening_progress_updated', 'user_awakening_progress', ['updated_at'])


def downgrade():
    """Drop awakening system tables and indexes"""
    
    # Drop indexes first
    op.drop_index('idx_user_awakening_progress_updated', table_name='user_awakening_progress')
    op.drop_index('idx_user_awakening_progress_streak', table_name='user_awakening_progress')
    op.drop_index('idx_user_awakening_progress_user', table_name='user_awakening_progress')
    
    op.drop_index('idx_awakening_rewards_created', table_name='awakening_rewards')
    op.drop_index('idx_awakening_rewards_type', table_name='awakening_rewards')
    op.drop_index('idx_awakening_rewards_quest', table_name='awakening_rewards')
    op.drop_index('idx_awakening_rewards_user', table_name='awakening_rewards')
    op.drop_index('idx_awakening_rewards_session', table_name='awakening_rewards')
    
    op.drop_index('idx_awakening_quests_type', table_name='awakening_quests')
    op.drop_index('idx_awakening_quests_difficulty', table_name='awakening_quests')
    op.drop_index('idx_awakening_quests_completed', table_name='awakening_quests')
    op.drop_index('idx_awakening_quests_movement', table_name='awakening_quests')
    op.drop_index('idx_awakening_quests_session', table_name='awakening_quests')
    
    op.drop_index('idx_awakening_sessions_readiness', table_name='awakening_sessions')
    op.drop_index('idx_awakening_sessions_created_at', table_name='awakening_sessions')
    op.drop_index('idx_awakening_sessions_user_completed', table_name='awakening_sessions')
    op.drop_index('idx_awakening_sessions_user_date', table_name='awakening_sessions')
    
    # Drop tables in reverse order (due to foreign key constraints)
    op.drop_table('user_awakening_progress')
    op.drop_table('awakening_rewards')
    op.drop_table('awakening_quests')
    op.drop_table('awakening_sessions')