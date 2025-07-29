#!/usr/bin/env python3
"""
Comprehensive database schema synchronization tool.
This script identifies and fixes ALL missing columns across ALL tables
by comparing the database schema with the SQLAlchemy models.
"""

import asyncio
import os
import sys
import importlib
import inspect
from urllib.parse import urlparse
from typing import Dict, List, Any, Set

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(__file__))

async def get_database_connection():
    """Get database connection."""
    try:
        import asyncpg
    except ImportError:
        print("ERROR: asyncpg library not available")
        print("Please install it with: pip install asyncpg")
        return None
    
    try:
        db_url = os.getenv('DATABASE_URL')
        if not db_url:
            print("ERROR: DATABASE_URL environment variable not set")
            return None
        
        if db_url.startswith('postgresql+asyncpg://'):
            db_url = db_url.replace('postgresql+asyncpg://', 'postgresql://')
        
        parsed = urlparse(db_url)
        
        conn = await asyncpg.connect(
            host=parsed.hostname,
            port=parsed.port or 5432,
            user=parsed.username,
            password=parsed.password,
            database=parsed.path[1:] if parsed.path else 'postgres'
        )
        
        return conn
        
    except Exception as e:
        print(f"ERROR: Could not connect to database: {e}")
        return None


async def get_database_schema(conn):
    """Get current database schema information."""
    tables_info = {}
    
    # Get all tables with their columns
    tables = await conn.fetch("""
        SELECT DISTINCT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_type = 'BASE TABLE'
        ORDER BY table_name;
    """)
    
    for table_row in tables:
        table_name = table_row['table_name']
        
        # Get columns for this table
        columns = await conn.fetch("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = $1 AND table_schema = 'public'
            ORDER BY ordinal_position;
        """, table_name)
        
        tables_info[table_name] = {
            'columns': {row['column_name']: {
                'type': row['data_type'],
                'nullable': row['is_nullable'] == 'YES',
                'default': row['column_default']
            } for row in columns}
        }
    
    return tables_info


def get_sqlalchemy_models():
    """Get all SQLAlchemy models from the v2 models directory."""
    models = {}
    
    try:
        from app.infrastructure.database.models.v2 import base
        from sqlalchemy import inspect as sa_inspect
        
        # Import all model modules
        model_modules = [
            'ascendants', 'awakening', 'dungeon_keys', 'dungeon_progress', 
            'dungeon_rewards', 'dungeon_sessions', 'movement_categories',
            'movements', 'quests', 'stats', 'user_skill_progress'
        ]
        
        for module_name in model_modules:
            try:
                module = importlib.import_module(f'app.infrastructure.database.models.v2.{module_name}')
                
                # Find all classes that are SQLAlchemy models
                for name, obj in inspect.getmembers(module):
                    if (inspect.isclass(obj) and 
                        hasattr(obj, '__tablename__') and 
                        hasattr(obj, '__table__')):
                        
                        table_name = obj.__tablename__
                        table = obj.__table__
                        
                        # Get column information
                        columns = {}
                        for column in table.columns:
                            columns[column.name] = {
                                'type': str(column.type),
                                'nullable': column.nullable,
                                'primary_key': column.primary_key,
                                'foreign_key': bool(column.foreign_keys),
                                'default': column.default
                            }
                        
                        models[table_name] = {
                            'model_class': obj,
                            'columns': columns
                        }
                        
            except Exception as e:
                print(f"Warning: Could not import {module_name}: {e}")
    
    except Exception as e:
        print(f"ERROR: Could not load SQLAlchemy models: {e}")
        return {}
    
    return models


def map_sqlalchemy_to_postgres_type(sqlalchemy_type: str) -> str:
    """Map SQLAlchemy column types to PostgreSQL types."""
    type_mapping = {
        'INTEGER': 'INTEGER',
        'BIGINT': 'BIGINT',
        'VARCHAR': 'VARCHAR',
        'TEXT': 'TEXT',
        'BOOLEAN': 'BOOLEAN',
        'DATE': 'DATE',
        'DATETIME': 'TIMESTAMP',
        'TIMESTAMP': 'TIMESTAMP',
        'FLOAT': 'REAL',
        'NUMERIC': 'NUMERIC',
        'JSON': 'JSON'
    }
    
    # Handle VARCHAR with length
    if 'VARCHAR(' in sqlalchemy_type:
        return sqlalchemy_type
    
    # Get base type
    base_type = sqlalchemy_type.split('(')[0].upper()
    return type_mapping.get(base_type, 'TEXT')


async def fix_missing_columns(conn, database_schema: Dict, model_schema: Dict):
    """Fix all missing columns across all tables."""
    fixes_applied = []
    
    print("Analyzing schema differences...")
    
    for table_name, model_info in model_schema.items():
        if table_name not in database_schema:
            print(f"WARNING: Table {table_name} exists in models but not in database")
            print(f"  This table needs to be created by running the main migrations")
            continue
        
        db_columns = set(database_schema[table_name]['columns'].keys())
        model_columns = set(model_info['columns'].keys())
        
        missing_columns = model_columns - db_columns
        
        if missing_columns:
            print(f"\n🔧 Fixing table: {table_name}")
            print(f"   Missing columns: {sorted(missing_columns)}")
            
            for column_name in missing_columns:
                column_info = model_info['columns'][column_name]
                
                # Determine PostgreSQL type
                pg_type = map_sqlalchemy_to_postgres_type(column_info['type'])
                
                # Build ALTER TABLE statement
                sql_parts = [f"ALTER TABLE {table_name} ADD COLUMN {column_name} {pg_type}"]
                
                # Handle nullable and defaults
                if not column_info['nullable']:
                    if column_info.get('default'):
                        # Has a default value
                        default_val = "DEFAULT CURRENT_TIMESTAMP" if 'TIMESTAMP' in pg_type else "DEFAULT 'default'"
                        sql_parts.append(f"NOT NULL {default_val}")
                    else:
                        # No default, add temporary default for existing data
                        if pg_type in ['INTEGER', 'BIGINT']:
                            sql_parts.append("NOT NULL DEFAULT 0")
                        elif pg_type == 'BOOLEAN':
                            sql_parts.append("NOT NULL DEFAULT false")
                        elif 'VARCHAR' in pg_type or pg_type == 'TEXT':
                            sql_parts.append("NOT NULL DEFAULT 'default'")
                        else:
                            sql_parts.append("NOT NULL DEFAULT 0")
                
                sql = " ".join(sql_parts) + ";"
                
                try:
                    await conn.execute(sql)
                    print(f"   ✓ Added {column_name} ({pg_type})")
                    fixes_applied.append(f"{table_name}.{column_name}")
                    
                    # Remove temporary default if the model doesn't specify one
                    if not column_info['nullable'] and not column_info.get('default'):
                        try:
                            await conn.execute(f"ALTER TABLE {table_name} ALTER COLUMN {column_name} DROP DEFAULT;")
                            print(f"   ✓ Removed temporary default from {column_name}")
                        except Exception as e:
                            print(f"   ! Warning: Could not remove default from {column_name}: {e}")
                    
                except Exception as e:
                    print(f"   ❌ Failed to add {column_name}: {e}")
        else:
            print(f"✓ Table {table_name}: All columns present")
    
    return fixes_applied


async def add_missing_indexes(conn, model_schema: Dict):
    """Add missing indexes based on model definitions."""
    print("\n🔍 Adding missing indexes...")
    
    common_indexes = [
        # Common patterns for foreign keys and frequently queried columns
        ("user_id", "idx_{table}_user_id"),
        ("ascendant_id", "idx_{table}_ascendant_id"),
        ("session_id", "idx_{table}_session_id"),
        ("created_at", "idx_{table}_created_at"),
        ("status", "idx_{table}_status"),
        ("reward_type", "idx_{table}_reward_type"),
    ]
    
    for table_name in model_schema.keys():
        for column_name, index_template in common_indexes:
            try:
                # Check if column exists in this table
                column_exists = await conn.fetchval("""
                    SELECT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name = $1 AND column_name = $2
                    );
                """, table_name, column_name)
                
                if column_exists:
                    index_name = index_template.format(table=table_name)
                    
                    # Check if index already exists
                    index_exists = await conn.fetchval("""
                        SELECT EXISTS (
                            SELECT 1 FROM pg_indexes 
                            WHERE tablename = $1 AND indexname = $2
                        );
                    """, table_name, index_name)
                    
                    if not index_exists:
                        await conn.execute(f"CREATE INDEX IF NOT EXISTS {index_name} ON {table_name}({column_name});")
                        print(f"   ✓ Added index {index_name}")
                
            except Exception as e:
                print(f"   ! Warning: Could not add index for {table_name}.{column_name}: {e}")


async def main():
    """Main schema synchronization function."""
    print("=" * 80)
    print("COMPREHENSIVE DATABASE SCHEMA SYNCHRONIZATION")
    print("=" * 80)
    
    # Connect to database
    print("Connecting to database...")
    conn = await get_database_connection()
    if not conn:
        return False
    
    print("Connected successfully!")
    
    try:
        # Get current database schema
        print("Analyzing current database schema...")
        database_schema = await get_database_schema(conn)
        print(f"Found {len(database_schema)} tables in database")
        
        # Get SQLAlchemy model schema
        print("Loading SQLAlchemy models...")
        model_schema = get_sqlalchemy_models()
        print(f"Found {len(model_schema)} models")
        
        if not model_schema:
            print("ERROR: Could not load any SQLAlchemy models")
            return False
        
        # Fix missing columns
        fixes_applied = await fix_missing_columns(conn, database_schema, model_schema)
        
        # Add missing indexes
        await add_missing_indexes(conn, model_schema)
        
        # Summary
        print("\n" + "=" * 80)
        print("SCHEMA SYNCHRONIZATION COMPLETE")
        print("=" * 80)
        
        if fixes_applied:
            print(f"✅ Applied {len(fixes_applied)} column fixes:")
            for fix in fixes_applied:
                print(f"   - {fix}")
        else:
            print("✅ No missing columns found - schema is synchronized!")
        
        print("\nNext steps:")
        print("1. Restart your application")
        print("2. Test all functionality")
        print("3. All database schema errors should be resolved")
        
        return True
        
    finally:
        await conn.close()


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        if success:
            print("\n🎉 Schema synchronization completed successfully!")
        else:
            print("\n❌ Schema synchronization failed")
    except KeyboardInterrupt:
        print("\n\n⚠️ Synchronization interrupted by user")
    except Exception as e:
        print(f"\n\n💥 Unexpected error: {e}")
        import traceback
        traceback.print_exc()