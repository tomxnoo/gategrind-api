# Awakening Sessions User ID Column Fix Guide

## Issue Summary

The application is failing with the error:
```
column awakening_sessions.user_id does not exist
```

This happens during user registration because the `awakening_sessions` table is missing the `user_id` column, which is required by the `AwakeningSession` model.

## Root Cause

The issue occurs when:
1. The Alembic migration that adds the `user_id` column hasn't been properly applied
2. The database schema is out of sync with the application models
3. The migration was applied but failed silently due to database connectivity issues

## Solutions (Try in Order)

### Solution 1: Re-run Migrations

```bash
# Apply all pending migrations
alembic upgrade head

# If that doesn't work, check current migration status
alembic current
alembic history --verbose
```

### Solution 2: Manual Database Fix (if database is accessible)

If you can connect to PostgreSQL directly:

```sql
-- Check if column exists
SELECT column_name FROM information_schema.columns 
WHERE table_name = 'awakening_sessions' AND column_name = 'user_id';

-- If it doesn't exist, add it manually
ALTER TABLE awakening_sessions ADD COLUMN user_id INTEGER NOT NULL DEFAULT 1;
ALTER TABLE awakening_sessions ADD CONSTRAINT fk_awakening_sessions_user_id 
    FOREIGN KEY (user_id) REFERENCES ascendants(id);
CREATE INDEX idx_awakening_sessions_user_id ON awakening_sessions(user_id);

-- Remove the default value after adding constraint
ALTER TABLE awakening_sessions ALTER COLUMN user_id DROP DEFAULT;
```

### Solution 3: Create New Migration

If the existing migration is problematic, create a new one:

```bash
# Generate a new migration specifically for this fix
alembic revision -m "fix_awakening_sessions_user_id_column"
```

Then edit the generated migration file to include:

```python
def upgrade() -> None:
    """Add user_id column to awakening_sessions if not exists."""
    op.execute("""
        DO $$ BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'awakening_sessions' 
                AND column_name = 'user_id'
            ) THEN
                ALTER TABLE awakening_sessions 
                ADD COLUMN user_id INTEGER NOT NULL DEFAULT 1;
                
                ALTER TABLE awakening_sessions 
                ADD CONSTRAINT fk_awakening_sessions_user_id 
                FOREIGN KEY (user_id) REFERENCES ascendants(id);
                
                CREATE INDEX idx_awakening_sessions_user_id ON awakening_sessions(user_id);
                
                -- Remove default after adding constraint
                ALTER TABLE awakening_sessions ALTER COLUMN user_id DROP DEFAULT;
            END IF;
        END $$;
    """)
```

### Solution 4: Use the Fix Script

Run the provided Python fix script:

```bash
python fix_awakening_schema_issue.py
```

This script will:
- Check if the database is accessible
- Verify the current schema state
- Add the missing column if needed
- Validate the fix worked

## Verification

After applying any fix, verify it worked:

1. **Check the database directly** (if accessible):
   ```sql
   \d awakening_sessions
   ```

2. **Test the application**:
   - Start the FastAPI server
   - Try to register a new user
   - Check that no "column does not exist" errors occur

3. **Check logs**:
   - Look for successful registration logs
   - Ensure no PostgreSQL errors related to awakening_sessions

## Environment-Specific Notes

### Replit/Cloud Environment
- Database might be managed externally
- Use the web-based database console if available
- Check environment variables for DATABASE_URL

### Local Development
- Ensure PostgreSQL is running: `pg_ctl status` or `systemctl status postgresql`
- Check connection with: `psql -h localhost -U user -d test_db`

### Docker Environment
- Check if database is in a container: `docker ps`
- Connect to database container: `docker exec -it <container> psql -U user -d db`

## Prevention

To prevent this issue in the future:

1. **Always test migrations** on a copy of production data
2. **Use migration rollback tests** to ensure they work both ways
3. **Add schema validation** to application startup
4. **Monitor migration logs** for any warnings or errors

## Files Modified/Created

- `fix_awakening_schema_issue.py` - Automated fix script
- `alembic/versions/55b1f7d935f3_add_missing_user_id_to_awakening_.py` - Existing migration
- This guide: `AWAKENING_SESSIONS_FIX_GUIDE.md`

## Quick Fix Command

If you just want to try the most likely solution:

```bash
# This should work in most cases
alembic upgrade head && python -c "print('Migration applied successfully')"
```

Then restart your application and test user registration.