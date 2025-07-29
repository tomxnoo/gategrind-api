"""fix_ascendant_id_integer_overflow_and_add_missing_columns

Revision ID: 40a013621c94
Revises: d7571156d2dc
Create Date: 2025-07-28 22:44:49.425470

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '40a013621c94'
down_revision: Union[str, Sequence[str], None] = 'd7571156d2dc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema to fix integer overflow issues and add missing columns."""
    
    # Fix integer overflow by changing ascendant_id from INTEGER to BIGINT
    # These tables need their ascendant_id foreign key columns updated
    
    tables_to_fix = [
        'ascendant_stats',
        'user_skill_progress', 
        'quests',
        'quest_completions',
        'dungeon_progress',
        'dungeon_keys',
        'dungeon_sessions',
        'dungeon_rewards'
    ]
    
    # Drop foreign key constraints first
    for table in tables_to_fix:
        op.drop_constraint(f"{table}_ascendant_id_fkey", table, type_="foreignkey")
    
    # Change column types to BIGINT
    for table in tables_to_fix:
        op.alter_column(table, 'ascendant_id', type_=sa.BigInteger, existing_nullable=False)
    
    # Recreate foreign key constraints
    for table in tables_to_fix:
        op.create_foreign_key(
            f"{table}_ascendant_id_fkey", 
            table, 
            'ascendants', 
            ['ascendant_id'], 
            ['id'],
            ondelete='CASCADE' if table != 'user_skill_progress' else None
        )
    
    # Add missing source column to quests table if it doesn't exist
    # Check if column exists first
    conn = op.get_bind()
    result = conn.execute(sa.text("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name='quests' AND column_name='source'
    """))
    
    if not result.fetchone():
        op.add_column('quests', sa.Column('source', sa.String(50), nullable=False, server_default='Unknown'))
        op.create_index('ix_quests_source', 'quests', ['source'])


def downgrade() -> None:
    """Downgrade schema - revert changes."""
    
    # Remove source column from quests if it was added
    conn = op.get_bind()
    result = conn.execute(sa.text("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name='quests' AND column_name='source'
    """))
    
    if result.fetchone():
        op.drop_index('ix_quests_source', 'quests')
        op.drop_column('quests', 'source')
    
    # Revert BIGINT back to INTEGER for ascendant_id columns
    tables_to_revert = [
        'ascendant_stats',
        'user_skill_progress', 
        'quests',
        'quest_completions',
        'dungeon_progress',
        'dungeon_keys',
        'dungeon_sessions',
        'dungeon_rewards'
    ]
    
    # Drop foreign key constraints
    for table in tables_to_revert:
        op.drop_constraint(f"{table}_ascendant_id_fkey", table, type_="foreignkey")
    
    # Change column types back to INTEGER
    for table in tables_to_revert:
        op.alter_column(table, 'ascendant_id', type_=sa.Integer, existing_nullable=False)
    
    # Recreate foreign key constraints
    for table in tables_to_revert:
        op.create_foreign_key(
            f"{table}_ascendant_id_fkey", 
            table, 
            'ascendants', 
            ['ascendant_id'], 
            ['id'],
            ondelete='CASCADE' if table != 'user_skill_progress' else None
        )
