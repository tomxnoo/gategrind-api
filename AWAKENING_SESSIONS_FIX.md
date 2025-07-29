# Awakening Sessions Database Schema Fix

## Problem Summary

The application is experiencing a critical database error:

```
column awakening_sessions.user_id does not exist
```

This error occurs during user registration when the system tries to query the `awakening_sessions` table for existing user data. The SQLAlchemy model expects a `user_id` column that doesn't exist in the actual database table.

## Root Cause Analysis

1. **Model vs Database Mismatch**: The `AwakeningSession` SQLAlchemy model (in `app/infrastructure/database/models/v2/awakening.py`) defines a `user_id` column:
   ```python
   user_id = Column(Integer, ForeignKey("ascendants.id"), nullable=False, index=True)
   ```

2. **Missing Migration**: The database schema doesn't include this column, indicating that either:
   - A migration was never created for this column
   - A migration failed to apply properly
   - The database was created without running all migrations

3. **Error Location**: The error occurs in `app/api/v2/auth.py` at line 42 during user registration when calling:
   ```python
   existing_user = await user_service.get_user_by_discord_id(registration.discord_id)
   ```

## Impact Assessment

- **Severity**: HIGH - User registration is completely broken
- **Affected Features**: 
  - User registration via Discord
  - Profile creation and retrieval
  - Awakening system functionality
- **User Experience**: Users cannot register or access the system

## Solution Implementation

### 1. Migration File Created

Created migration file: `alembic/versions/55b1f7d935f3_add_missing_user_id_to_awakening_.py`

The migration includes:
- Safe column addition with existence check
- Foreign key constraint to `ascendants` table
- Performance index creation
- Proper rollback functionality

### 2. Diagnostic Tool

Created `fix_awakening_sessions_schema.py` for:
- Database schema validation
- Migration status checking
- Automated fix application
- Verification of solutions

## Fix Application Steps

### Option 1: Automated Fix (Recommended)

```bash
# Check the current schema status
python fix_awakening_sessions_schema.py --check-only

# Apply the fix automatically
python fix_awakening_sessions_schema.py --apply-fix
```

### Option 2: Manual Fix

```bash
# 1. Check current migration status
alembic current

# 2. Apply the migration
alembic upgrade head

# 3. Verify the fix
python fix_awakening_sessions_schema.py --check-only
```

### Option 3: Direct Database Fix (Emergency Only)

If migrations cannot be applied, manually add the column:

```sql
-- Connect to PostgreSQL database
-- Add the user_id column
ALTER TABLE awakening_sessions 
ADD COLUMN user_id INTEGER NOT NULL;

-- Add foreign key constraint
ALTER TABLE awakening_sessions 
ADD CONSTRAINT fk_awakening_sessions_user_id 
FOREIGN KEY (user_id) REFERENCES ascendants(id);

-- Add performance index
CREATE INDEX idx_awakening_sessions_user_id ON awakening_sessions(user_id);
```

**⚠️ Warning**: Manual database changes should be avoided in production environments.

## Verification Steps

After applying the fix:

1. **Schema Verification**:
   ```bash
   python fix_awakening_sessions_schema.py --check-only
   ```

2. **Application Testing**:
   - Start the application: `python app/main.py`
   - Test user registration via Discord bot
   - Verify profile creation works

3. **Database Verification**:
   ```sql
   \d awakening_sessions  -- Should show user_id column
   SELECT * FROM awakening_sessions LIMIT 1;  -- Should work without errors
   ```

## Prevention Measures

To prevent similar issues in the future:

1. **Migration Validation**: Always verify migrations apply successfully:
   ```bash
   alembic upgrade head
   alembic current  # Verify current revision
   ```

2. **Schema Testing**: Add automated tests that verify critical columns exist:
   ```python
   async def test_awakening_sessions_schema():
       # Test that user_id column exists and is properly configured
       pass
   ```

3. **Development Workflow**: 
   - Run `alembic upgrade head` after pulling changes
   - Verify application starts without database errors
   - Test critical user flows after schema changes

## Files Modified/Created

- ✅ **Created**: `alembic/versions/55b1f7d935f3_add_missing_user_id_to_awakening_.py`
- ✅ **Created**: `fix_awakening_sessions_schema.py` (diagnostic tool)
- ✅ **Created**: `AWAKENING_SESSIONS_FIX.md` (this documentation)

## Migration Details

**Migration ID**: `55b1f7d935f3`  
**Revises**: `6916a40b7c5c`  
**Description**: Add missing user_id column to awakening_sessions table

The migration uses PostgreSQL's `DO $$ ... $$` blocks to safely add the column only if it doesn't exist, preventing duplicate column errors if run multiple times.

## Contact and Support

If issues persist after applying this fix:

1. Check database connectivity and permissions
2. Verify PostgreSQL is running and accessible
3. Ensure DATABASE_URL environment variable is correct
4. Review application logs for additional error details
5. Consider running database integrity checks

---

**Status**: ✅ SOLUTION READY - Apply migration to resolve issue  
**Priority**: HIGH - Critical system functionality affected  
**Estimated Fix Time**: 2-5 minutes