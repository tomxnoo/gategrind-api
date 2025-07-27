"""add_missing_v2_tables_comprehensive

Revision ID: ca162ef54cde
Revises: 27c2c20a1311
Create Date: 2025-07-28 00:12:13.091485

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ca162ef54cde'
down_revision: Union[str, Sequence[str], None] = '27c2c20a1311'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add all missing V2 tables to synchronize database with expected schema."""
    
    # Create stat_enum type if it doesn't exist
    op.execute("CREATE TYPE IF NOT EXISTS stat_enum AS ENUM ('STR', 'END', 'TECH')")
    
    # 1. Create movement_categories table
    op.create_table('movement_categories',
        sa.Column('id', sa.String(50), primary_key=True, nullable=False),
        sa.Column('name', sa.String(100), unique=True, nullable=False),
        sa.Column('primary_stat', sa.Enum('STR', 'END', 'TECH', name='stat_enum'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    
    # 2. Create movements table
    op.create_table('movements',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('node_id', sa.Integer, sa.ForeignKey('skill_tree_nodes.id'), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('xp_per_rep', sa.Float, default=1.0, nullable=False),
        sa.Column('stat_reward_type', sa.Enum('STR', 'END', 'TECH', name='stat_enum'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    
    # 3. Create ascendant_stats table
    op.create_table('ascendant_stats',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('ascendant_id', sa.Integer, sa.ForeignKey('ascendants.id', ondelete='CASCADE'), unique=True, nullable=False),
        sa.Column('str_level', sa.Integer, default=1, nullable=False),
        sa.Column('str_xp', sa.Float, default=0.0, nullable=False),
        sa.Column('end_level', sa.Integer, default=1, nullable=False),
        sa.Column('end_xp', sa.Float, default=0.0, nullable=False),
        sa.Column('tech_level', sa.Integer, default=1, nullable=False),
        sa.Column('tech_xp', sa.Float, default=0.0, nullable=False),
        sa.Column('str_value', sa.Integer, default=10, nullable=False),
        sa.Column('end_value', sa.Integer, default=10, nullable=False),
        sa.Column('tech_value', sa.Integer, default=10, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.CheckConstraint('str_level >= 1', name='check_str_level_positive'),
        sa.CheckConstraint('str_xp >= 0', name='check_str_xp_non_negative'),
        sa.CheckConstraint('end_level >= 1', name='check_end_level_positive'),
        sa.CheckConstraint('end_xp >= 0', name='check_end_xp_non_negative'),
        sa.CheckConstraint('tech_level >= 1', name='check_tech_level_positive'),
        sa.CheckConstraint('tech_xp >= 0', name='check_tech_xp_non_negative'),
        sa.CheckConstraint('str_value >= 1', name='check_str_value_positive'),
        sa.CheckConstraint('end_value >= 1', name='check_end_value_positive'),
        sa.CheckConstraint('tech_value >= 1', name='check_tech_value_positive'),
    )
    
    # 4. Create quests table
    op.create_table('quests',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('ascendant_id', sa.Integer, sa.ForeignKey('ascendants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.String),
        sa.Column('source', sa.String(50), nullable=False),
        sa.Column('status', sa.String(20), default='active', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    
    # 5. Create quest_completions table
    op.create_table('quest_completions',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('ascendant_id', sa.Integer, sa.ForeignKey('ascendants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('quest_id', sa.Integer, sa.ForeignKey('quests.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    
    # 6. Create dungeon_trials table
    op.create_table('dungeon_trials',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('session_id', sa.Integer, sa.ForeignKey('dungeon_sessions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('trial_number', sa.Integer, nullable=False),
        sa.Column('trial_type', sa.String(50), nullable=False),
        sa.Column('status', sa.String(20), default='pending', nullable=False),
        sa.Column('start_time', sa.DateTime(timezone=True)),
        sa.Column('end_time', sa.DateTime(timezone=True)),
        sa.Column('result', sa.String(20)),
        sa.Column('score', sa.Float),
        sa.Column('details', sa.Text),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.CheckConstraint('trial_number >= 1', name='check_trial_number_positive'),
        sa.CheckConstraint('score >= 0', name='check_score_non_negative'),
    )
    
    # 7. Create dungeon_rewards table
    op.create_table('dungeon_rewards',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('ascendant_id', sa.Integer, sa.ForeignKey('ascendants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('session_id', sa.Integer, sa.ForeignKey('dungeon_sessions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('reward_type', sa.String(50), nullable=False),
        sa.Column('quantity', sa.Integer, default=0, nullable=False),
        sa.Column('bonus_multiplier', sa.Float, default=1.0, nullable=False),
        sa.Column('awarded_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.CheckConstraint('quantity >= 0', name='check_quantity_non_negative'),
        sa.CheckConstraint('bonus_multiplier >= 0', name='check_bonus_multiplier_non_negative'),
    )
    
    # 8. Create daily_modifiers table
    op.create_table('daily_modifiers',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('date', sa.Date, unique=True, nullable=False),
        sa.Column('modifier_type', sa.String(50), nullable=False),
        sa.Column('value', sa.Float, nullable=False),
        sa.Column('description', sa.String(255)),
        sa.Column('is_active', sa.Boolean, default=True, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    
    # 9. Create dungeon_level_unlocks table
    op.create_table('dungeon_level_unlocks',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('level', sa.Integer, unique=True, nullable=False),
        sa.Column('required_aura', sa.Integer, nullable=False),
        sa.Column('required_level', sa.Integer, nullable=False),
        sa.Column('is_active', sa.Boolean, default=True, nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.CheckConstraint('level >= 1', name='check_level_positive'),
        sa.CheckConstraint('required_aura >= 0', name='check_required_aura_non_negative'),
        sa.CheckConstraint('required_level >= 1', name='check_required_level_positive'),
    )
    
    # 10. Create awakening_sessions table
    op.create_table('awakening_sessions',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('ascendants.id'), nullable=False),
        sa.Column('session_date', sa.Date, nullable=False),
        sa.Column('tier_level', sa.String(20), nullable=False, default='normal'),
        sa.Column('status', sa.String(20), nullable=False, default='active'),
        sa.Column('reset_used', sa.Boolean, nullable=False, default=False),
        sa.Column('reset_at', sa.DateTime(timezone=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True)),
    )
    
    # 11. Create awakening_quests table
    op.create_table('awakening_quests',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('session_id', sa.Integer, sa.ForeignKey('awakening_sessions.id'), nullable=False),
        sa.Column('quest_type', sa.String(50), nullable=False),
        sa.Column('target_movement_id', sa.Integer),
        sa.Column('target_movement', sa.String(100)),
        sa.Column('target_reps', sa.Integer),
        sa.Column('target_time', sa.Integer),
        sa.Column('target_distance', sa.Integer),
        sa.Column('difficulty_level', sa.String(20), nullable=False, default='moderate'),
        sa.Column('parameters', sa.JSON),
        sa.Column('status', sa.String(20), nullable=False, default='active'),
        sa.Column('progress_reps', sa.Integer, nullable=False, default=0),
        sa.Column('progress_time', sa.Integer, nullable=False, default=0),
        sa.Column('progress_distance', sa.Integer, nullable=False, default=0),
        sa.Column('completed_at', sa.DateTime(timezone=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    
    # 12. Create awakening_rewards table
    op.create_table('awakening_rewards',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('session_id', sa.Integer, sa.ForeignKey('awakening_sessions.id'), nullable=False),
        sa.Column('shadow_keys', sa.Integer, nullable=False, default=0),
        sa.Column('xp_gained', sa.Integer, nullable=False, default=0),
        sa.Column('stat_points', sa.Integer, nullable=False, default=0),
        sa.Column('aura_change', sa.Integer, nullable=False, default=0),
        sa.Column('streak_bonus', sa.Integer, nullable=False, default=0),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    
    # 13. Create user_awakening_progress table
    op.create_table('user_awakening_progress',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer, nullable=False),
        sa.Column('quest_id', sa.Integer, sa.ForeignKey('awakening_quests.id'), nullable=False),
        sa.Column('progress_reps', sa.Integer, nullable=False, default=0),
        sa.Column('progress_time', sa.Integer, nullable=False, default=0),
        sa.Column('progress_distance', sa.Integer, nullable=False, default=0),
        sa.Column('last_updated', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True)),
        sa.Column('rewards_claimed', sa.Boolean, nullable=False, default=False),
    )
    
    # Create indexes for performance
    op.create_index('idx_movements_node_id', 'movements', ['node_id'])
    op.create_index('idx_movements_name', 'movements', ['name'])
    op.create_index('idx_movements_node_name_unique', 'movements', ['node_id', 'name'], unique=True)
    
    op.create_index('idx_ascendant_stats_ascendant_id', 'ascendant_stats', ['ascendant_id'])
    
    op.create_index('idx_quests_ascendant_status', 'quests', ['ascendant_id', 'status'])
    op.create_index('idx_quests_source', 'quests', ['source'])
    op.create_index('idx_quests_status', 'quests', ['status'])
    
    op.create_index('idx_quest_completions_ascendant_date', 'quest_completions', ['ascendant_id', 'created_at'])
    
    op.create_index('idx_dungeon_trials_session_id', 'dungeon_trials', ['session_id'])
    op.create_index('idx_dungeon_trials_status', 'dungeon_trials', ['status'])
    
    op.create_index('idx_dungeon_rewards_ascendant_id', 'dungeon_rewards', ['ascendant_id'])
    op.create_index('idx_dungeon_rewards_session_id', 'dungeon_rewards', ['session_id'])
    
    op.create_index('idx_daily_modifiers_date', 'daily_modifiers', ['date'])
    op.create_index('idx_daily_modifiers_type', 'daily_modifiers', ['modifier_type'])
    
    op.create_index('idx_dungeon_level_unlocks_level', 'dungeon_level_unlocks', ['level'])
    
    op.create_index('idx_awakening_sessions_user_date', 'awakening_sessions', ['user_id', 'session_date'])
    op.create_index('idx_awakening_sessions_status', 'awakening_sessions', ['status'])
    op.create_index('idx_awakening_sessions_user_id', 'awakening_sessions', ['user_id'])
    
    op.create_index('idx_awakening_quests_session', 'awakening_quests', ['session_id'])
    op.create_index('idx_awakening_quests_type_status', 'awakening_quests', ['quest_type', 'status'])
    op.create_index('idx_awakening_quests_movement', 'awakening_quests', ['target_movement_id'])
    op.create_index('idx_awakening_quests_status', 'awakening_quests', ['status'])
    
    op.create_index('idx_awakening_rewards_session', 'awakening_rewards', ['session_id'])
    
    op.create_index('idx_user_awakening_progress_user_quest', 'user_awakening_progress', ['user_id', 'quest_id'])
    op.create_index('idx_user_awakening_progress_completed', 'user_awakening_progress', ['completed_at'])
    op.create_index('idx_user_awakening_progress_user_id', 'user_awakening_progress', ['user_id'])


def downgrade() -> None:
    """Remove all V2 tables added in this migration."""
    
    # Drop tables in reverse order to handle foreign key dependencies
    op.drop_table('user_awakening_progress')
    op.drop_table('awakening_rewards')
    op.drop_table('awakening_quests')
    op.drop_table('awakening_sessions')
    op.drop_table('dungeon_level_unlocks')
    op.drop_table('daily_modifiers')
    op.drop_table('dungeon_rewards')
    op.drop_table('dungeon_trials')
    op.drop_table('quest_completions')
    op.drop_table('quests')
    op.drop_table('ascendant_stats')
    op.drop_table('movements')
    op.drop_table('movement_categories')
    
    # Drop the enum type
    op.execute("DROP TYPE IF EXISTS stat_enum")
