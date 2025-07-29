"""add_missing_user_id_to_awakening_sessions

Revision ID: 55b1f7d935f3
Revises: 6916a40b7c5c
Create Date: 2025-07-29 00:00:21.498901

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '55b1f7d935f3'
down_revision: Union[str, Sequence[str], None] = '6916a40b7c5c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - Add missing user_id column to awakening_sessions table."""
    # Check if user_id column already exists to avoid duplicate column error
    op.execute("""
        DO $$ BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'awakening_sessions' 
                AND column_name = 'user_id'
            ) THEN
                ALTER TABLE awakening_sessions 
                ADD COLUMN user_id INTEGER NOT NULL;
                
                -- Add foreign key constraint
                ALTER TABLE awakening_sessions 
                ADD CONSTRAINT fk_awakening_sessions_user_id 
                FOREIGN KEY (user_id) REFERENCES ascendants(id);
                
                -- Add index for performance
                CREATE INDEX idx_awakening_sessions_user_id ON awakening_sessions(user_id);
            END IF;
        END $$;
    """)


def downgrade() -> None:
    """Downgrade schema - Remove user_id column from awakening_sessions table."""
    # Drop the column and its constraints/indexes
    op.execute("""
        DO $$ BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'awakening_sessions' 
                AND column_name = 'user_id'
            ) THEN
                -- Drop index first
                DROP INDEX IF EXISTS idx_awakening_sessions_user_id;
                
                -- Drop foreign key constraint
                ALTER TABLE awakening_sessions 
                DROP CONSTRAINT IF EXISTS fk_awakening_sessions_user_id;
                
                -- Drop the column
                ALTER TABLE awakening_sessions DROP COLUMN user_id;
            END IF;
        END $$;
    """)
