"""Add all missing columns and tables

Revision ID: fix_all_missing_cols
Revises: create_system_settings
Create Date: 2025-01-28 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'fix_all_missing_cols'
down_revision = 'create_system_settings'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Get database connection to check existing columns
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    
    # Check and add missing columns to ascendant_stats
    existing_columns = [col['name'] for col in inspector.get_columns('ascendant_stats')]
    
    if 'str_value' not in existing_columns:
        op.add_column('ascendant_stats', sa.Column('str_value', sa.Integer(), nullable=False, server_default='10'))
    if 'end_value' not in existing_columns:
        op.add_column('ascendant_stats', sa.Column('end_value', sa.Integer(), nullable=False, server_default='10'))
    if 'tech_value' not in existing_columns:
        op.add_column('ascendant_stats', sa.Column('tech_value', sa.Integer(), nullable=False, server_default='10'))
    
    # Add constraints for stat values (check if they don't exist)
    try:
        op.create_check_constraint('check_str_value_positive', 'ascendant_stats', 'str_value >= 1')
    except:
        pass
    try:
        op.create_check_constraint('check_end_value_positive', 'ascendant_stats', 'end_value >= 1')
    except:
        pass
    try:
        op.create_check_constraint('check_tech_value_positive', 'ascendant_stats', 'tech_value >= 1')
    except:
        pass
    
    # Check existing tables
    existing_tables = inspector.get_table_names()
    
    # Create awakening_sessions table if it doesn't exist
    if 'awakening_sessions' not in existing_tables:
        op.create_table('awakening_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('session_date', sa.Date(), nullable=False),
        sa.Column('tier_level', sa.String(length=20), nullable=False, server_default='normal'),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='active'),
        sa.Column('reset_used', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('reset_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['ascendants.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
        op.create_index('idx_awakening_sessions_user_date', 'awakening_sessions', ['user_id', 'session_date'])
        op.create_index('idx_awakening_sessions_status', 'awakening_sessions', ['status'])
    
    # Create awakening_quests table if it doesn't exist
    if 'awakening_quests' not in existing_tables:
        op.create_table('awakening_quests',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.Integer(), nullable=False),
        sa.Column('quest_type', sa.String(length=50), nullable=False),
        sa.Column('target_movement_id', sa.Integer(), nullable=True),
        sa.Column('target_movement', sa.String(length=100), nullable=True),
        sa.Column('target_reps', sa.Integer(), nullable=True),
        sa.Column('target_time', sa.Integer(), nullable=True),
        sa.Column('target_distance', sa.Integer(), nullable=True),
        sa.Column('difficulty_level', sa.String(length=20), nullable=False, server_default='moderate'),
        sa.Column('parameters', sa.JSON(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='active'),
        sa.Column('progress_reps', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('progress_time', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('progress_distance', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['session_id'], ['awakening_sessions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
        op.create_index('idx_awakening_quests_session', 'awakening_quests', ['session_id'])
        op.create_index('idx_awakening_quests_type_status', 'awakening_quests', ['quest_type', 'status'])
        op.create_index('idx_awakening_quests_movement', 'awakening_quests', ['target_movement_id'])
    
    # Create awakening_rewards table if it doesn't exist
    if 'awakening_rewards' not in existing_tables:
        op.create_table('awakening_rewards',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.Integer(), nullable=False),
        sa.Column('shadow_keys', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('xp_gained', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('stat_points', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('aura_change', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('streak_bonus', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['session_id'], ['awakening_sessions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
        op.create_index('idx_awakening_rewards_session', 'awakening_rewards', ['session_id'])
    
    # Create user_awakening_progress table if it doesn't exist
    if 'user_awakening_progress' not in existing_tables:
        op.create_table('user_awakening_progress',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('quest_id', sa.Integer(), nullable=False),
        sa.Column('progress_reps', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('progress_time', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('progress_distance', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('last_updated', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('rewards_claimed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['quest_id'], ['awakening_quests.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
        op.create_index('idx_user_awakening_progress_user_quest', 'user_awakening_progress', ['user_id', 'quest_id'])
        op.create_index('idx_user_awakening_progress_completed', 'user_awakening_progress', ['completed_at'])


def downgrade() -> None:
    # Get database connection to check existing tables/columns
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    existing_tables = inspector.get_table_names()
    
    # Drop awakening tables if they exist
    if 'user_awakening_progress' in existing_tables:
        op.drop_index('idx_user_awakening_progress_completed', table_name='user_awakening_progress')
        op.drop_index('idx_user_awakening_progress_user_quest', table_name='user_awakening_progress')
        op.drop_table('user_awakening_progress')
    
    if 'awakening_rewards' in existing_tables:
        op.drop_index('idx_awakening_rewards_session', table_name='awakening_rewards')
        op.drop_table('awakening_rewards')
    
    if 'awakening_quests' in existing_tables:
        op.drop_index('idx_awakening_quests_movement', table_name='awakening_quests')
        op.drop_index('idx_awakening_quests_type_status', table_name='awakening_quests')
        op.drop_index('idx_awakening_quests_session', table_name='awakening_quests')
        op.drop_table('awakening_quests')
    
    if 'awakening_sessions' in existing_tables:
        op.drop_index('idx_awakening_sessions_status', table_name='awakening_sessions')
        op.drop_index('idx_awakening_sessions_user_date', table_name='awakening_sessions')
        op.drop_table('awakening_sessions')
    
    # Remove constraints from ascendant_stats (if they exist)
    try:
        op.drop_constraint('check_tech_value_positive', 'ascendant_stats', type_='check')
    except:
        pass
    try:
        op.drop_constraint('check_end_value_positive', 'ascendant_stats', type_='check')
    except:
        pass
    try:
        op.drop_constraint('check_str_value_positive', 'ascendant_stats', type_='check')
    except:
        pass
    
    # Remove columns from ascendant_stats if they exist
    if 'ascendant_stats' in existing_tables:
        existing_columns = [col['name'] for col in inspector.get_columns('ascendant_stats')]
        if 'tech_value' in existing_columns:
            op.drop_column('ascendant_stats', 'tech_value')
        if 'end_value' in existing_columns:
            op.drop_column('ascendant_stats', 'end_value')
        if 'str_value' in existing_columns:
            op.drop_column('ascendant_stats', 'str_value')