#!/usr/bin/env python3

import os
import asyncio
import asyncpg
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def get_db_connection():
    """Get database connection."""
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        raise ValueError("DATABASE_URL not found in environment variables")
    
    return await asyncpg.connect(database_url)

async def find_all_categories_to_fix():
    """Find all categories that have both movements and skill tree nodes."""
    
    conn = await get_db_connection()
    
    try:
        print("🔍 Finding all categories that need movement distribution fixes...\n")
        
        # Find categories that have both movements and skill tree nodes
        categories = await conn.fetch("""
            SELECT DISTINCT 
                mc.id as category_id,
                mc.name as category_name,
                COUNT(DISTINCT m.id) as movement_count,
                COUNT(DISTINCT stn.node_id) as skill_node_count,
                COUNT(DISTINCT CASE WHEN stn.level = 1 THEN m.id END) as level_1_movements,
                COUNT(DISTINCT CASE WHEN stn.level > 1 THEN m.id END) as higher_level_movements
            FROM movement_categories mc
            LEFT JOIN movements m ON mc.id = m.category_id
            LEFT JOIN skill_tree_nodes stn ON mc.id = stn.category_id
            LEFT JOIN movements m2 ON stn.node_id = m2.node_id
            WHERE m.id IS NOT NULL AND stn.node_id IS NOT NULL
            GROUP BY mc.id, mc.name
            HAVING COUNT(DISTINCT m.id) > 0 AND COUNT(DISTINCT stn.node_id) > 0
            ORDER BY mc.id;
        """)
        
        print("📊 Categories with movements and skill tree nodes:")
        print("=" * 80)
        
        categories_to_fix = []
        
        for cat in categories:
            category_id = str(cat['category_id'])
            category_name = cat['category_name']
            movement_count = cat['movement_count']
            skill_node_count = cat['skill_node_count']
            level_1_movements = cat['level_1_movements'] or 0
            higher_level_movements = cat['higher_level_movements'] or 0
            
            # Check if this category needs fixing (all movements in level 1)
            needs_fixing = level_1_movements == movement_count and higher_level_movements == 0
            
            status = "🔴 NEEDS FIXING" if needs_fixing else "✅ LOOKS GOOD"
            
            print(f"Category {category_id}: {category_name}")
            print(f"  Movements: {movement_count} | Skill Nodes: {skill_node_count}")
            print(f"  Level 1: {level_1_movements} movements | Higher Levels: {higher_level_movements} movements")
            print(f"  Status: {status}")
            print()
            
            if needs_fixing:
                categories_to_fix.append((category_id, category_name))
        
        print(f"🎯 Found {len(categories_to_fix)} categories that need fixing:")
        for cat_id, cat_name in categories_to_fix:
            print(f"  - {cat_name} (ID: {cat_id})")
        
        return categories_to_fix
        
    finally:
        await conn.close()

async def check_skill_points_system():
    """Check if skill points system exists in the database."""
    
    conn = await get_db_connection()
    
    try:
        print("\n🔍 Checking for skill points system...\n")
        
        # Check user tables for skill points
        user_columns = await conn.fetch("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'users' 
            AND column_name ILIKE '%skill%' OR column_name ILIKE '%point%'
            ORDER BY column_name;
        """)
        
        print("👤 User table skill/point related columns:")
        if user_columns:
            for col in user_columns:
                print(f"  - {col['column_name']} ({col['data_type']})")
        else:
            print("  ❌ No skill/point columns found in users table")
        
        # Check skill tree nodes for point costs
        skill_node_columns = await conn.fetch("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'skill_tree_nodes'
            ORDER BY column_name;
        """)
        
        print("\n🌳 Skill tree nodes table columns:")
        for col in skill_node_columns:
            print(f"  - {col['column_name']} ({col['data_type']})")
        
        # Check user_skill_progress table
        progress_columns = await conn.fetch("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'user_skill_progress'
            ORDER BY column_name;
        """)
        
        print("\n📈 User skill progress table columns:")
        if progress_columns:
            for col in progress_columns:
                print(f"  - {col['column_name']} ({col['data_type']})")
        else:
            print("  ❌ user_skill_progress table not found")
        
        # Look for any tables with 'point' in the name
        point_tables = await conn.fetch("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_name ILIKE '%point%'
            ORDER BY table_name;
        """)
        
        print("\n💰 Tables with 'point' in name:")
        if point_tables:
            for table in point_tables:
                print(f"  - {table['table_name']}")
        else:
            print("  ❌ No tables with 'point' in name found")
        
    finally:
        await conn.close()

if __name__ == "__main__":
    async def main():
        categories_to_fix = await find_all_categories_to_fix()
        await check_skill_points_system()
        
        print(f"\n🎯 Summary:")
        print(f"  - {len(categories_to_fix)} categories need movement distribution fixes")
        print(f"  - Skill points system investigation completed")
    
    asyncio.run(main())