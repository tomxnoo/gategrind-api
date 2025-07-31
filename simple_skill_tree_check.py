#!/usr/bin/env python3
"""
Simple Skill Tree Node ID Check Script
For debugging the skill node ID mismatch issue

This script focuses on:
1. What skill node IDs exist in the database
2. What the API library endpoint returns
3. Comparing the two to find mismatches

Usage: python simple_skill_tree_check.py
"""

import asyncio
import json
from typing import Dict, List
import sys
sys.path.append('/home/runner/workspace')

from app.infrastructure.database.session import get_async_session
from sqlalchemy import text

async def check_skill_nodes():
    """Check skill node IDs in database vs API."""
    print("🔍 Checking skill node IDs...")
    
    async for session in get_async_session():
        try:
            # 1. Check what tables exist
            print("\n📋 Checking available tables...")
            tables_result = await session.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND (table_name LIKE '%skill%' OR table_name LIKE '%movement%' OR table_name LIKE '%unlock%')
                ORDER BY table_name;
            """))
            
            tables = [row[0] for row in tables_result.fetchall()]
            print(f"Available tables: {tables}")
            
            # 2. Check skill_tree_nodes table structure
            if 'skill_tree_nodes' in tables:
                print(f"\n📊 skill_tree_nodes table structure:")
                columns_result = await session.execute(text("""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = 'skill_tree_nodes' 
                    ORDER BY ordinal_position;
                """))
                
                columns = [(row[0], row[1]) for row in columns_result.fetchall()]
                for col_name, col_type in columns:
                    print(f"  - {col_name}: {col_type}")
                
                # Get sample data
                print(f"\n📝 Sample skill_tree_nodes data:")
                sample_result = await session.execute(text("""
                    SELECT * FROM skill_tree_nodes LIMIT 10;
                """))
                
                # Get column names for display
                col_names = [col[0] for col in columns]
                
                for i, row in enumerate(sample_result.fetchall()):
                    print(f"\n  Node {i+1}:")
                    for j, value in enumerate(row):
                        if j < len(col_names):
                            print(f"    {col_names[j]}: {value}")
            
            # 3. Check movements table
            if 'movements' in tables:
                print(f"\n📊 movements table structure:")
                movements_columns_result = await session.execute(text("""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = 'movements' 
                    ORDER BY ordinal_position;
                """))
                
                movements_columns = [(row[0], row[1]) for row in movements_columns_result.fetchall()]
                for col_name, col_type in movements_columns:
                    print(f"  - {col_name}: {col_type}")
                
                # Get sample movements data
                print(f"\n📝 Sample movements data:")
                movements_sample_result = await session.execute(text("""
                    SELECT * FROM movements LIMIT 5;
                """))
                
                movements_col_names = [col[0] for col in movements_columns]
                
                for i, row in enumerate(movements_sample_result.fetchall()):
                    print(f"\n  Movement {i+1}:")
                    for j, value in enumerate(row):
                        if j < len(movements_col_names):
                            print(f"    {movements_col_names[j]}: {value}")
            
            # 4. Check movement_categories table
            if 'movement_categories' in tables:
                print(f"\n📊 movement_categories table structure:")
                categories_columns_result = await session.execute(text("""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = 'movement_categories' 
                    ORDER BY ordinal_position;
                """))
                
                categories_columns = [(row[0], row[1]) for row in categories_columns_result.fetchall()]
                for col_name, col_type in categories_columns:
                    print(f"  - {col_name}: {col_type}")
                
                # Get all categories
                print(f"\n📝 All movement categories:")
                categories_result = await session.execute(text("""
                    SELECT * FROM movement_categories ORDER BY id;
                """))
                
                categories_col_names = [col[0] for col in categories_columns]
                
                for i, row in enumerate(categories_result.fetchall()):
                    print(f"\n  Category {i+1}:")
                    for j, value in enumerate(row):
                        if j < len(categories_col_names):
                            print(f"    {categories_col_names[j]}: {value}")
            
            # 5. Check for unlocked skills table
            unlocked_tables = [t for t in tables if 'unlock' in t or 'skill' in t]
            print(f"\n📋 Tables with 'unlock' or 'skill': {unlocked_tables}")
            
            for table in unlocked_tables:
                if table != 'skill_tree_nodes':  # Already checked above
                    try:
                        print(f"\n📊 {table} table structure:")
                        table_columns_result = await session.execute(text(f"""
                            SELECT column_name, data_type 
                            FROM information_schema.columns 
                            WHERE table_name = '{table}' 
                            ORDER BY ordinal_position;
                        """))
                        
                        table_columns = [(row[0], row[1]) for row in table_columns_result.fetchall()]
                        for col_name, col_type in table_columns:
                            print(f"  - {col_name}: {col_type}")
                        
                        # Get sample data
                        print(f"\n📝 Sample {table} data:")
                        table_sample_result = await session.execute(text(f"""
                            SELECT * FROM {table} LIMIT 3;
                        """))
                        
                        table_col_names = [col[0] for col in table_columns]
                        
                        for i, row in enumerate(table_sample_result.fetchall()):
                            print(f"\n  Row {i+1}:")
                            for j, value in enumerate(row):
                                if j < len(table_col_names):
                                    print(f"    {table_col_names[j]}: {value}")
                    except Exception as e:
                        print(f"  ⚠️  Error accessing {table}: {e}")
            
            # 6. Specific check for the problematic node ID
            print(f"\n🔍 Searching for 'pull_unilateral_1' node ID...")
            
            # Try different possible locations
            search_queries = [
                "SELECT * FROM skill_tree_nodes WHERE id LIKE '%pull%' OR id LIKE '%unilateral%';",
                "SELECT * FROM movements WHERE id LIKE '%pull%' OR name LIKE '%pull%';",
                "SELECT * FROM skill_tree_nodes WHERE name LIKE '%pull%' OR name LIKE '%unilateral%';"
            ]
            
            for query in search_queries:
                try:
                    print(f"\n  Query: {query}")
                    search_result = await session.execute(text(query))
                    rows = search_result.fetchall()
                    if rows:
                        print(f"  Found {len(rows)} results:")
                        for row in rows:
                            print(f"    {row}")
                    else:
                        print("  No results found")
                except Exception as e:
                    print(f"  Error: {e}")
            
            print(f"\n✅ Database check complete!")
            break
            
        except Exception as e:
            print(f"❌ Error during check: {e}")
            import traceback
            traceback.print_exc()
            break

async def main():
    """Main execution function."""
    print("🚀 Starting Simple Skill Tree Node ID Check")
    print("=" * 50)
    
    await check_skill_nodes()

if __name__ == "__main__":
    asyncio.run(main())