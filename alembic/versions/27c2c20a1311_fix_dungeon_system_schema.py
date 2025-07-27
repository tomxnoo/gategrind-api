"""fix_dungeon_system_schema

Revision ID: 27c2c20a1311
Revises: 420833bb84cb
Create Date: 2025-07-28 00:06:36.358877

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '27c2c20a1311'
down_revision: Union[str, Sequence[str], None] = '420833bb84cb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add indexes for better performance on dungeon-related queries
    
    # Ensure proper indexing on dungeon_keys table
    try:
        op.create_index('idx_dungeon_keys_ascendant_type', 'dungeon_keys', ['ascendant_id', 'key_type'], unique=False)
    except Exception:
        pass  # Index might already exist
    
    # Ensure proper indexing on dungeon_progress table
    try:
        op.create_index('idx_dungeon_progress_ascendant', 'dungeon_progress', ['ascendant_id'], unique=False)
    except Exception:
        pass  # Index might already exist
    
    # Ensure proper indexing on ascendants table for dungeon-related fields
    try:
        op.create_index('idx_ascendants_shadow_keys', 'ascendants', ['shadow_keys'], unique=False)
    except Exception:
        pass  # Index might already exist
    
    try:
        op.create_index('idx_ascendants_level', 'ascendants', ['level'], unique=False)
    except Exception:
        pass  # Index might already exist
    
    try:
        op.create_index('idx_ascendants_aura', 'ascendants', ['aura'], unique=False)
    except Exception:
        pass  # Index might already exist


def downgrade() -> None:
    """Downgrade schema."""
    # Remove the indexes we added
    try:
        op.drop_index('idx_dungeon_keys_ascendant_type', table_name='dungeon_keys')
    except Exception:
        pass
    
    try:
        op.drop_index('idx_dungeon_progress_ascendant', table_name='dungeon_progress')
    except Exception:
        pass
    
    try:
        op.drop_index('idx_ascendants_shadow_keys', table_name='ascendants')
    except Exception:
        pass
    
    try:
        op.drop_index('idx_ascendants_level', table_name='ascendants')
    except Exception:
        pass
    
    try:
        op.drop_index('idx_ascendants_aura', table_name='ascendants')
    except Exception:
        pass
