import asyncio
import os
from sqlalchemy import create_engine, inspect, MetaData
from sqlalchemy.ext.asyncio import create_async_engine
import asyncpg

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://localhost/test")

# Convert to sync URL for inspection
if DATABASE_URL.startswith("postgresql+asyncpg://"):
    sync_url = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
else:
    sync_url = DATABASE_URL

async def check_tables():
    # Connect and get table info
    engine = create_engine(sync_url)
    inspector = inspect(engine)
    
    # Get all tables
    tables = inspector.get_table_names()
    print(f"Found {len(tables)} tables in database")
    
    # Check specific tables for missing columns
    tables_to_check = {
        'ascendant_stats': ['str_value', 'end_value', 'tech_value'],
        'dungeon_progress': ['total_completions', 'total_shadow_keys_spent', 'total_shadow_essence_earned', 'last_completion_date', 'best_completion_time'],
        'dungeon_sessions': ['shadow_keys_spent', 'session_status', 'trial_data', 'daily_modifier_id'],
        'awakening_sessions': [],  # Check if exists
        'awakening_quests': [],    # Check if exists
        'awakening_rewards': [],   # Check if exists
        'user_awakening_progress': []  # Check if exists
    }
    
    missing_info = {}
    
    for table_name, expected_cols in tables_to_check.items():
        if table_name in tables:
            columns = [col['name'] for col in inspector.get_columns(table_name)]
            if expected_cols:
                missing = [col for col in expected_cols if col not in columns]
                if missing:
                    missing_info[table_name] = missing
                    print(f"\nTable '{table_name}' missing columns: {missing}")
            else:
                print(f"\nTable '{table_name}' exists with columns: {columns[:5]}...")
        else:
            missing_info[table_name] = "TABLE_MISSING"
            print(f"\nTable '{table_name}' does not exist\!")
    
    return missing_info

if __name__ == "__main__":
    asyncio.run(check_tables())


## Alembic Migration Timeout & Autoincrement Warning - Analysis & Solutions
Based on my analysis using VisionCraft MCP and Ref MCP , I've identified the root causes and comprehensive solutions for your Alembic migration timeout issue.

### 🔍 Root Cause Analysis
1. Migration Complexity Issue:

- The `d7571156d2dc_add_missing_value_columns_to_ascendant_.py` migration is extremely large (802 lines)
- Performs complex operations: column type changes, index rebuilding, foreign key constraint modifications
- Multiple BIGINT → Integer conversions that require full table scans and data validation
2. Timeout Configuration:

- No timeout settings in `env.py`
- Using default PostgreSQL timeouts (insufficient for large operations)
3. Autoincrement Warning:

- MySQL-specific autoincrement and existing_autoincrement parameters being used in PostgreSQL context
- PostgreSQL uses SERIAL / IDENTITY types, not MySQL autoincrement syntax
4. Critical Schema Conflict:

- ⚠️ MAJOR ISSUE : This migration reverts BIGINT back to Integer for ascendant_id columns
- This will reintroduce the Discord ID overflow errors from your console log
- Conflicts with the required fixes for 64-bit Discord Snowflake IDs
### 🛠️ Solutions (VisionCraft MCP + Ref MCP) Solution 1: Immediate Timeout Fix
Update `env.py` to add PostgreSQL timeout configurations:

```
def run_migrations_online() -> None:
    """Run migrations in 'online' mode 
    with timeout configurations."""
    connectable = engine_from_config(
        config.get_section(config.
        config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as 
    connection:
        # Set PostgreSQL timeouts for 
        large migrations
        connection.execute(text("SET 
        statement_timeout TO '30min'"))
        connection.execute(text("SET 
        lock_timeout TO '5min'"))
        connection.execute(text("SET 
        idle_in_transaction_session_timeout
         TO '60min'"))
        
        context.configure(
            connection=connection, 
            target_metadata=target_metadata
            ,
            compare_type=True,
            compare_server_default=True,
            transaction_per_migration=True,
              # Smaller transactions
        )

        with context.begin_transaction():
            context.run_migrations()
``` Solution 2: Fix Autoincrement Warning
The warning occurs because the migration uses MySQL-specific parameters. For PostgreSQL, remove these parameters and let PostgreSQL handle SERIAL types automatically.
 Solution 3: Address Schema Conflict (CRITICAL)
⚠️ Before proceeding with the migration, you need to decide:

Option A: Skip This Migration (Recommended)

```
# Mark migration as applied without 
running it
alembic stamp d7571156d2dc
```
Option B: Fix the Migration The migration should maintain BIGINT for Discord IDs, not revert to Integer . This requires editing the migration file.

Option C: Break Down the Migration Split the 802-line migration into smaller, focused migrations:

1. 1.
   Index operations only
2. 2.
   Column additions only
3. 3.
   Type changes only
4. 4.
   Constraint modifications only Solution 4: Alternative Approach - Reset and Rebuild
If the migration conflicts are too complex:

```
# 1. Backup current database
pg_dump your_database > backup.sql

# 2. Reset to previous working state
alembic downgrade fix_all_missing_cols

# 3. Create new, targeted migrations for 
specific fixes
alembic revision --autogenerate -m 
"fix_discord_id_bigint_only"
```
### 🎯 Recommended Action Plan
1. 1.
   Immediate Fix : Apply Solution 1 (timeout configuration) to `env.py`
2. 2.
   Critical Decision : Determine if this migration should run at all, since it reverts the BIGINT fixes needed for Discord IDs
3. 3.
   Long-term : Break down large migrations into smaller, focused operations
4. 4.
   Validation : After any migration, verify that Discord ID fields remain as BIGINT to prevent overflow errors
### 📋 VisionCraft MCP Key Insights Applied:
- ✅ Set PostgreSQL-specific timeouts ( statement_timeout , lock_timeout )
- ✅ Use transaction_per_migration=True for smaller transactions
- ✅ Proper PostgreSQL SERIAL / IDENTITY handling instead of MySQL autoincrement
- ✅ Break down large migrations to prevent table locks
### 📋 Ref MCP Key Findings Applied:
- ✅ Identified schema conflict with Discord ID BIGINT requirements
- ✅ Located the problematic migration file and operations
- ✅ Confirmed current Alembic configuration lacks timeout settings
Would you like me to implement the timeout fix first, or would you prefer to address the schema conflict issue before proceeding?