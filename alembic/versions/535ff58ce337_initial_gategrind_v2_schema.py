"""initial_gategrind_v2_schema

Revision ID: 535ff58ce337
Revises: 
Create Date: 2025-07-28 21:43:11.775547

Complete V2 schema migration for GateGrind with all tables, enums, and indexes.
This is a clean migration for the fresh GateGrind database.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '535ff58ce337'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - Create complete V2 database schema."""
    
    # Create ENUM types with manual existence check
    conn = op.get_bind()
    
    # Check and create incursiontype enum
    result = conn.execute(sa.text("SELECT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'incursiontype')"))
    if not result.scalar():
        incursion_type_enum = postgresql.ENUM('surge', 'challenge', 'anomaly', name='incursiontype')
        incursion_type_enum.create(conn)
    
    # Check and create rewardtype enum
    result = conn.execute(sa.text("SELECT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'rewardtype')"))
    if not result.scalar():
        reward_type_enum = postgresql.ENUM('xp', 'buff', 'item', name='rewardtype')
        reward_type_enum.create(conn)
    
    # Check and create incursionstatus enum
    result = conn.execute(sa.text("SELECT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'incursionstatus')"))
    if not result.scalar():
        incursion_status_enum = postgresql.ENUM('active', 'completed', 'expired', name='incursionstatus')
        incursion_status_enum.create(conn)
    
    # Create ascendants table (core user table)
    op.create_table('ascendants',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('discord_id', sa.String(length=20), nullable=False),
        sa.Column('username', sa.String(length=100), nullable=False),
        sa.Column('level', sa.Integer(), nullable=False, default=1),
        sa.Column('global_xp', sa.Integer(), nullable=False, default=0),
        sa.Column('aura', sa.Integer(), nullable=False, default=0),
        sa.Column('skill_points', sa.Integer(), nullable=False, default=0),
        sa.Column('strength_points', sa.Integer(), nullable=False, default=0),
        sa.Column('endurance_points', sa.Integer(), nullable=False, default=0),
        sa.Column('technique_points', sa.Integer(), nullable=False, default=0),
        sa.Column('shadow_keys', sa.Integer(), nullable=False, default=0),
        sa.Column('rested_xp_pool', sa.Integer(), nullable=False, default=0),
        sa.Column('last_login', sa.DateTime(timezone=True), nullable=True),
        sa.Column('awakening_streak', sa.Integer(), nullable=False, default=0),
        sa.Column('last_reset_date', sa.Date(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_ascendant_aura', 'ascendants', ['aura'])
    op.create_index('idx_ascendant_discord_id', 'ascendants', ['discord_id'])
    op.create_index('idx_ascendant_global_xp', 'ascendants', ['global_xp'])
    op.create_index('idx_ascendant_last_login', 'ascendants', ['last_login'])
    op.create_index('idx_ascendant_level', 'ascendants', ['level'])
    op.create_index(op.f('ix_ascendants_discord_id'), 'ascendants', ['discord_id'], unique=True)
    op.create_index(op.f('ix_ascendants_id'), 'ascendants', ['id'])

    # Create ascendant_stats table
    op.create_table('ascendant_stats',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('ascendant_id', sa.BigInteger(), nullable=False),
        sa.Column('str_level', sa.Integer(), nullable=False, default=1),
        sa.Column('str_xp', sa.Integer(), nullable=False, default=0),
        sa.Column('end_level', sa.Integer(), nullable=False, default=1),
        sa.Column('end_xp', sa.Integer(), nullable=False, default=0),
        sa.Column('tech_level', sa.Integer(), nullable=False, default=1),
        sa.Column('tech_xp', sa.Integer(), nullable=False, default=0),
        sa.ForeignKeyConstraint(['ascendant_id'], ['ascendants.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ascendant_stats_id'), 'ascendant_stats', ['id'])

    # Create movement_categories table
    op.create_table('movement_categories',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('category_id', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_movement_categories_category_id'), 'movement_categories', ['category_id'], unique=True)
    op.create_index(op.f('ix_movement_categories_id'), 'movement_categories', ['id'])

    # Create skill_tree_nodes table
    op.create_table('skill_tree_nodes',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('node_id', sa.String(length=50), nullable=False),
        sa.Column('category_id', sa.String(length=50), nullable=False),
        sa.Column('level', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('ascendant_level_required', sa.Integer(), nullable=False, default=1),
        sa.Column('stat_points_required', sa.Integer(), nullable=False, default=1),
        sa.ForeignKeyConstraint(['category_id'], ['movement_categories.category_id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_skill_tree_nodes_id'), 'skill_tree_nodes', ['id'])
    op.create_index(op.f('ix_skill_tree_nodes_node_id'), 'skill_tree_nodes', ['node_id'], unique=True)

    # Create movements table
    op.create_table('movements',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('node_id', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('xp_per_rep', sa.Integer(), nullable=False, default=1),
        sa.ForeignKeyConstraint(['node_id'], ['skill_tree_nodes.node_id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_movements_id'), 'movements', ['id'])

    # Create user_skill_progress table
    op.create_table('user_skill_progress',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('ascendant_id', sa.BigInteger(), nullable=False),
        sa.Column('node_id', sa.String(length=50), nullable=False),
        sa.Column('unlocked_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['ascendant_id'], ['ascendants.id'], ),
        sa.ForeignKeyConstraint(['node_id'], ['skill_tree_nodes.node_id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('ascendant_id', 'node_id', name='uq_user_skill_progress_ascendant_node')
    )
    op.create_index('idx_user_skill_progress_ascendant_id', 'user_skill_progress', ['ascendant_id'])
    op.create_index('idx_user_skill_progress_node_id', 'user_skill_progress', ['node_id'])
    op.create_index(op.f('ix_user_skill_progress_id'), 'user_skill_progress', ['id'])

    # Create quests table
    op.create_table('quests',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('ascendant_id', sa.BigInteger(), nullable=False),
        sa.Column('quest_id', sa.String(length=50), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('target_exercise', sa.String(length=100), nullable=False),
        sa.Column('target_reps', sa.Integer(), nullable=False),
        sa.Column('xp_reward', sa.Integer(), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['ascendant_id'], ['ascendants.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_quests_ascendant_id', 'quests', ['ascendant_id'])
    op.create_index('idx_quests_expires_at', 'quests', ['expires_at'])
    op.create_index(op.f('ix_quests_id'), 'quests', ['id'])
    op.create_index(op.f('ix_quests_quest_id'), 'quests', ['quest_id'], unique=True)

    # Create quest_completions table
    op.create_table('quest_completions',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('ascendant_id', sa.BigInteger(), nullable=False),
        sa.Column('quest_id', sa.String(length=50), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('xp_earned', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['ascendant_id'], ['ascendants.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_quest_completions_ascendant_id', 'quest_completions', ['ascendant_id'])
    op.create_index('idx_quest_completions_completed_at', 'quest_completions', ['completed_at'])
    op.create_index(op.f('ix_quest_completions_id'), 'quest_completions', ['id'])

    # Create dungeon_keys table
    op.create_table('dungeon_keys',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('ascendant_id', sa.BigInteger(), nullable=False),
        sa.Column('key_type', sa.String(length=50), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False, default=0),
        sa.ForeignKeyConstraint(['ascendant_id'], ['ascendants.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_dungeon_keys_ascendant_id', 'dungeon_keys', ['ascendant_id'])
    op.create_index(op.f('ix_dungeon_keys_id'), 'dungeon_keys', ['id'])

    # Create dungeon_progress table
    op.create_table('dungeon_progress',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('ascendant_id', sa.BigInteger(), nullable=False),
        sa.Column('highest_level_completed', sa.Integer(), nullable=False, default=0),
        sa.Column('last_completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['ascendant_id'], ['ascendants.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_dungeon_progress_ascendant_id', 'dungeon_progress', ['ascendant_id'])
    op.create_index(op.f('ix_dungeon_progress_id'), 'dungeon_progress', ['id'])

    # Create dungeon_sessions table
    op.create_table('dungeon_sessions',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('ascendant_id', sa.BigInteger(), nullable=False),
        sa.Column('session_id', sa.String(length=50), nullable=False),
        sa.Column('dungeon_level', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False, default='active'),
        sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('session_data', postgresql.JSON(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.ForeignKeyConstraint(['ascendant_id'], ['ascendants.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_dungeon_sessions_ascendant_id', 'dungeon_sessions', ['ascendant_id'])
    op.create_index('idx_dungeon_sessions_status', 'dungeon_sessions', ['status'])
    op.create_index(op.f('ix_dungeon_sessions_id'), 'dungeon_sessions', ['id'])
    op.create_index(op.f('ix_dungeon_sessions_session_id'), 'dungeon_sessions', ['session_id'], unique=True)

    # Create dungeon_trials table
    op.create_table('dungeon_trials',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('session_id', sa.BigInteger(), nullable=False),
        sa.Column('trial_number', sa.Integer(), nullable=False),
        sa.Column('exercise_name', sa.String(length=100), nullable=False),
        sa.Column('target_reps', sa.Integer(), nullable=False),
        sa.Column('completed_reps', sa.Integer(), nullable=False, default=0),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_completed', sa.Boolean(), nullable=False, default=False),
        sa.ForeignKeyConstraint(['session_id'], ['dungeon_sessions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_dungeon_trials_session_id', 'dungeon_trials', ['session_id'])
    op.create_index(op.f('ix_dungeon_trials_id'), 'dungeon_trials', ['id'])

    # Create dungeon_rewards table
    op.create_table('dungeon_rewards',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('ascendant_id', sa.BigInteger(), nullable=False),
        sa.Column('session_id', sa.BigInteger(), nullable=False),
        sa.Column('reward_type', sa.String(length=50), nullable=False),
        sa.Column('reward_value', sa.Integer(), nullable=False),
        sa.Column('earned_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['ascendant_id'], ['ascendants.id'], ),
        sa.ForeignKeyConstraint(['session_id'], ['dungeon_sessions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_dungeon_rewards_ascendant_id', 'dungeon_rewards', ['ascendant_id'])
    op.create_index(op.f('ix_dungeon_rewards_id'), 'dungeon_rewards', ['id'])

    # Create daily_modifiers table
    op.create_table('daily_modifiers',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('modifier_name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('difficulty_multiplier', sa.Float(), nullable=False, default=1.0),
        sa.Column('reward_multiplier', sa.Float(), nullable=False, default=1.0),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_daily_modifiers_date', 'daily_modifiers', ['date'])
    op.create_index(op.f('ix_daily_modifiers_id'), 'daily_modifiers', ['id'])

    # Create dungeon_level_unlocks table
    op.create_table('dungeon_level_unlocks',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('ascendant_id', sa.BigInteger(), nullable=False),
        sa.Column('dungeon_level', sa.Integer(), nullable=False),
        sa.Column('unlocked_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['ascendant_id'], ['ascendants.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_dungeon_level_unlocks_ascendant_id', 'dungeon_level_unlocks', ['ascendant_id'])
    op.create_index(op.f('ix_dungeon_level_unlocks_id'), 'dungeon_level_unlocks', ['id'])

    # Create incursions_v2 table
    op.create_table('incursions_v2',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('incursion_id', sa.String(length=50), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('incursion_type', postgresql.ENUM('surge', 'challenge', 'anomaly', name='incursiontype', create_type=False), nullable=False),
        sa.Column('status', postgresql.ENUM('active', 'completed', 'expired', name='incursionstatus', create_type=False), nullable=False, default='active'),
        sa.Column('target_exercise', sa.String(length=100), nullable=False),
        sa.Column('target_reps', sa.Integer(), nullable=False),
        sa.Column('current_reps', sa.Integer(), nullable=False, default=0),
        sa.Column('reward_type', postgresql.ENUM('xp', 'buff', 'item', name='rewardtype', create_type=False), nullable=False),
        sa.Column('reward_value', sa.Integer(), nullable=False),
        sa.Column('reward_description', sa.String(length=500), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('extra_data', postgresql.JSON(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_incursions_v2_id'), 'incursions_v2', ['id'])
    op.create_index(op.f('ix_incursions_v2_incursion_id'), 'incursions_v2', ['incursion_id'], unique=True)

    # Create incursion_participants_v2 table
    op.create_table('incursion_participants_v2',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('incursion_id', sa.BigInteger(), nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('reps_contributed', sa.Integer(), nullable=False, default=0),
        sa.Column('participated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['incursion_id'], ['incursions_v2.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_incursion_participants_v2_id'), 'incursion_participants_v2', ['id'])

    # Create awakening_sessions table
    op.create_table('awakening_sessions',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('ascendant_id', sa.BigInteger(), nullable=False),
        sa.Column('session_date', sa.Date(), nullable=False),
        sa.Column('is_completed', sa.Boolean(), nullable=False, default=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['ascendant_id'], ['ascendants.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_awakening_sessions_id'), 'awakening_sessions', ['id'])

    # Create awakening_quests table
    op.create_table('awakening_quests',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('session_id', sa.BigInteger(), nullable=False),
        sa.Column('quest_type', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('target_value', sa.Integer(), nullable=False),
        sa.Column('current_progress', sa.Integer(), nullable=False, default=0),
        sa.Column('is_completed', sa.Boolean(), nullable=False, default=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['session_id'], ['awakening_sessions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_awakening_quests_id'), 'awakening_quests', ['id'])

    # Create awakening_rewards table
    op.create_table('awakening_rewards',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('session_id', sa.BigInteger(), nullable=False),
        sa.Column('reward_type', sa.String(length=50), nullable=False),
        sa.Column('reward_value', sa.Integer(), nullable=False),
        sa.Column('earned_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['session_id'], ['awakening_sessions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_awakening_rewards_id'), 'awakening_rewards', ['id'])

    # Create user_awakening_progress table
    op.create_table('user_awakening_progress',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('ascendant_id', sa.BigInteger(), nullable=False),
        sa.Column('total_sessions', sa.Integer(), nullable=False, default=0),
        sa.Column('current_streak', sa.Integer(), nullable=False, default=0),
        sa.Column('longest_streak', sa.Integer(), nullable=False, default=0),
        sa.Column('last_session_date', sa.Date(), nullable=True),
        sa.ForeignKeyConstraint(['ascendant_id'], ['ascendants.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_awakening_progress_id'), 'user_awakening_progress', ['id'])


def downgrade() -> None:
    """Downgrade schema - Drop all V2 tables and enums."""
    
    # Drop tables in reverse order (respecting foreign key constraints)
    op.drop_table('user_awakening_progress')
    op.drop_table('awakening_rewards')
    op.drop_table('awakening_quests')
    op.drop_table('awakening_sessions')
    op.drop_table('incursion_participants_v2')
    op.drop_table('incursions_v2')
    op.drop_table('dungeon_level_unlocks')
    op.drop_table('daily_modifiers')
    op.drop_table('dungeon_rewards')
    op.drop_table('dungeon_trials')
    op.drop_table('dungeon_sessions')
    op.drop_table('dungeon_progress')
    op.drop_table('dungeon_keys')
    op.drop_table('quest_completions')
    op.drop_table('quests')
    op.drop_table('user_skill_progress')
    op.drop_table('movements')
    op.drop_table('skill_tree_nodes')
    op.drop_table('movement_categories')
    op.drop_table('ascendant_stats')
    op.drop_table('ascendants')
    
    # Drop ENUM types with existence check
    incursion_status_enum = postgresql.ENUM('active', 'completed', 'expired', name='incursionstatus')
    incursion_status_enum.drop(op.get_bind(), checkfirst=True)
    
    reward_type_enum = postgresql.ENUM('xp', 'buff', 'item', name='rewardtype')
    reward_type_enum.drop(op.get_bind(), checkfirst=True)
    
    incursion_type_enum = postgresql.ENUM('surge', 'challenge', 'anomaly', name='incursiontype')
    incursion_type_enum.drop(op.get_bind(), checkfirst=True)
