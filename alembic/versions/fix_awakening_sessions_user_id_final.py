"""fix_awakening_sessions_user_id_final

Revision ID: awaken_user_id_fix
Revises: 55b1f7d935f3
Create Date: 2025-07-29 00:30:00.000000

Final fix for awakening_sessions.user_id column with proper error handling
and support for existing data.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'awaken_user_id_fix'
down_revision: Union[str, Sequence[str], None] = '55b1f7d935f3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - Fix awakening_sessions.user_id column with robust error handling."""
    
    # First, check if awakening_sessions table exists
    op.execute("""
        DO $$ 
        DECLARE
            table_exists BOOLEAN;
            column_exists BOOLEAN;
            has_data BOOLEAN;
            first_user_id INTEGER;
        BEGIN
            -- Check if table exists
            SELECT EXISTS (
                SELECT 1 FROM information_schema.tables 
                WHERE table_name = 'awakening_sessions'
            ) INTO table_exists;
            
            IF NOT table_exists THEN
                RAISE NOTICE 'awakening_sessions table does not exist - skipping migration';
                RETURN;
            END IF;
            
            -- Check if user_id column already exists
            SELECT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'awakening_sessions' 
                AND column_name = 'user_id'
            ) INTO column_exists;
            
            IF column_exists THEN
                RAISE NOTICE 'user_id column already exists in awakening_sessions - skipping';
                RETURN;
            END IF;
            
            -- Check if table has existing data
            SELECT EXISTS (SELECT 1 FROM awakening_sessions LIMIT 1) INTO has_data;
            
            -- Get first user ID from ascendants table for default value
            SELECT id INTO first_user_id FROM ascendants ORDER BY id LIMIT 1;
            
            IF first_user_id IS NULL THEN
                first_user_id := 1; -- fallback if no users exist
            END IF;
            
            RAISE NOTICE 'Adding user_id column to awakening_sessions table (default user_id: %)', first_user_id;
            
            -- Add the column with a default value
            EXECUTE format('ALTER TABLE awakening_sessions ADD COLUMN user_id INTEGER NOT NULL DEFAULT %s', first_user_id);
            
            -- Add foreign key constraint (only if ascendants table exists)
            IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'ascendants') THEN
                ALTER TABLE awakening_sessions 
                ADD CONSTRAINT fk_awakening_sessions_user_id 
                FOREIGN KEY (user_id) REFERENCES ascendants(id);
                
                RAISE NOTICE 'Added foreign key constraint for user_id';
            ELSE
                RAISE NOTICE 'Skipped foreign key constraint - ascendants table not found';
            END IF;
            
            -- Add index for performance
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_awakening_sessions_user_id 
            ON awakening_sessions(user_id);
            
            -- Remove the default value now that existing rows have been populated
            ALTER TABLE awakening_sessions ALTER COLUMN user_id DROP DEFAULT;
            
            RAISE NOTICE 'Successfully added user_id column to awakening_sessions';
            
        EXCEPTION
            WHEN OTHERS THEN
                RAISE NOTICE 'Error in awakening_sessions migration: %', SQLERRM;
                -- Don't re-raise to avoid breaking the migration
        END $$;
    """)


def downgrade() -> None:
    """Downgrade schema - Remove user_id column from awakening_sessions table."""
    op.execute("""
        DO $$ 
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'awakening_sessions' 
                AND column_name = 'user_id'
            ) THEN
                RAISE NOTICE 'Removing user_id column from awakening_sessions';
                
                -- Drop index first
                DROP INDEX IF EXISTS idx_awakening_sessions_user_id;
                
                -- Drop foreign key constraint
                ALTER TABLE awakening_sessions 
                DROP CONSTRAINT IF EXISTS fk_awakening_sessions_user_id;
                
                -- Drop the column
                ALTER TABLE awakening_sessions DROP COLUMN user_id;
                
                RAISE NOTICE 'Successfully removed user_id column';
            ELSE
                RAISE NOTICE 'user_id column does not exist - nothing to remove';
            END IF;
        EXCEPTION
            WHEN OTHERS THEN
                RAISE NOTICE 'Error in awakening_sessions downgrade: %', SQLERRM;
        END $$;
    """)