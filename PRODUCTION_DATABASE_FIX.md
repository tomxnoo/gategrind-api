# Production Database Migration Fix

## Issue Analysis

The `awakening_sessions.user_id does not exist` error is occurring because:
1. **Local migrations were applied successfully** (as confirmed by `alembic current` showing `awaken_user_id_fix`)
2. **Production/remote database is out of sync** - the migration hasn't been applied to the actual database the application is using
3. **Environment mismatch** - local dev environment vs. production/remote environment

## Evidence from Logs

```
Database: localhost/ros_db  # From config
[ERROR] column awakening_sessions.user_id does not exist  # Production error
```

The application is running in what appears to be a containerized environment (`/home/runner/workspace/`) but our local migrations were applied to a different database instance.

## Solutions

### Solution 1: Apply Migration to Production Database

If you have access to the production environment:

```bash
# Connect to the production environment and run:
alembic upgrade head

# Or specifically apply our fix:
alembic upgrade awaken_user_id_fix
```

### Solution 2: Manual Database Fix (Production)

If Alembic migrations can't be run in production, apply the SQL manually:

```sql
-- Connect to the production PostgreSQL database and run:
DO $$ BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'awakening_sessions' 
        AND column_name = 'user_id'
    ) THEN
        -- Add the missing column
        ALTER TABLE awakening_sessions 
        ADD COLUMN user_id INTEGER NOT NULL DEFAULT 1;
        
        -- Add foreign key constraint
        ALTER TABLE awakening_sessions 
        ADD CONSTRAINT fk_awakening_sessions_user_id 
        FOREIGN KEY (user_id) REFERENCES ascendants(id);
        
        -- Add index for performance
        CREATE INDEX idx_awakening_sessions_user_id ON awakening_sessions(user_id);
        
        -- Remove default after adding constraint
        ALTER TABLE awakening_sessions ALTER COLUMN user_id DROP DEFAULT;
        
        RAISE NOTICE 'Successfully added user_id column to awakening_sessions';
    ELSE
        RAISE NOTICE 'user_id column already exists';
    END IF;
END $$;
```

### Solution 3: Deployment Script

Create a deployment-safe script that can be run in any environment:

```bash
#!/bin/bash
# deploy_awakening_fix.sh

echo "Applying awakening_sessions.user_id fix..."

# Check if alembic is available
if command -v alembic &> /dev/null; then
    echo "Applying migration using Alembic..."
    alembic upgrade awaken_user_id_fix
    
    if [ $? -eq 0 ]; then
        echo "✅ Migration applied successfully"
        exit 0
    else
        echo "⚠️ Migration failed, trying manual approach..."
    fi
fi

# Fallback to manual SQL execution
echo "Applying manual SQL fix..."
python3 -c "
import asyncio
import os
from urllib.parse import urlparse
try:
    import asyncpg
    
    async def apply_fix():
        db_url = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost/ros_db')
        if db_url.startswith('postgresql+asyncpg://'):
            db_url = db_url.replace('postgresql+asyncpg://', 'postgresql://')
        
        parsed = urlparse(db_url)
        conn = await asyncpg.connect(
            host=parsed.hostname,
            port=parsed.port or 5432,
            user=parsed.username,
            password=parsed.password,
            database=parsed.path[1:] if parsed.path else 'ros_db'
        )
        
        await conn.execute('''
            DO \$\$ BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name = 'awakening_sessions' 
                    AND column_name = 'user_id'
                ) THEN
                    ALTER TABLE awakening_sessions ADD COLUMN user_id INTEGER NOT NULL DEFAULT 1;
                    ALTER TABLE awakening_sessions ADD CONSTRAINT fk_awakening_sessions_user_id 
                        FOREIGN KEY (user_id) REFERENCES ascendants(id);
                    CREATE INDEX idx_awakening_sessions_user_id ON awakening_sessions(user_id);
                    ALTER TABLE awakening_sessions ALTER COLUMN user_id DROP DEFAULT;
                    RAISE NOTICE 'Successfully added user_id column';
                ELSE
                    RAISE NOTICE 'user_id column already exists';
                END IF;
            END \$\$;
        ''')
        
        await conn.close()
        print('✅ Manual fix applied successfully')
    
    asyncio.run(apply_fix())
    
except ImportError:
    print('❌ asyncpg not available, please install it or use SQL directly')
except Exception as e:
    print(f'❌ Error: {e}')
"

echo "Fix deployment completed. Please restart your application."
```

### Solution 4: Application-Level Workaround (Temporary)

If database changes can't be applied immediately, modify the application to gracefully handle the missing column:

```python
# In app/application/services/awakening_service.py or similar
async def get_user_awakening_sessions(self, user_id: int):
    try:
        # Normal query with user_id
        return await self.session.execute(
            select(AwakeningSession).where(AwakeningSession.user_id == user_id)
        ).scalars().all()
    except Exception as e:
        if "column awakening_sessions.user_id does not exist" in str(e):
            # Fallback: return empty list or migrate on-the-fly
            logger.warning("awakening_sessions.user_id column missing - applying fix")
            await self._apply_schema_fix()
            # Retry the query
            return await self.session.execute(
                select(AwakeningSession).where(AwakeningSession.user_id == user_id)
            ).scalars().all()
        raise
```

## Recommended Approach

1. **Immediate**: Use Solution 2 (Manual SQL) to fix the production database
2. **Long-term**: Ensure migration pipeline applies to production environment
3. **Backup**: Keep Solution 4 as a safety net

## Environment-Specific Instructions

### For Replit/Cloud Environments
1. Open the database console in your cloud environment
2. Run the manual SQL from Solution 2
3. Restart the application

### For Docker/Container Environments
1. Access the container: `docker exec -it <container> bash`
2. Run: `alembic upgrade awaken_user_id_fix`
3. Or use the database console to run the SQL manually

### For Traditional Servers
1. SSH into the server
2. Navigate to the application directory
3. Run the migration or SQL fix
4. Restart the application service

## Verification

After applying the fix, verify it worked:

```bash
# Check the database schema
psql -d your_database -c "\d awakening_sessions"

# Should show user_id column in the output

# Or run the verification script
python test_awakening_fix.py
```

## Prevention

To prevent this in the future:
1. Set up automated migration deployment
2. Include database schema validation in startup
3. Use database migration health checks
4. Maintain environment parity between dev/staging/production