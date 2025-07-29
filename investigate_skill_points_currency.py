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

async def investigate_skill_points_system():
    """Investigate the SKILL POINTS currency system (not stat points)."""
    
    conn = await get_db_connection()
    
    try:
        print("🔍 INVESTIGATING SKILL POINTS CURRENCY SYSTEM")
        print("=" * 60)
        
        # 1. Check for skill point storage/tracking
        print("\n💰 1. SKILL POINT STORAGE & TRACKING")
        print("-" * 40)
        
        # Look for user skill point balance tables
        skill_point_tables = await conn.fetch("""
            SELECT table_name, column_name, data_type
            FROM information_schema.columns 
            WHERE (column_name ILIKE '%skill_point%' OR 
                   column_name ILIKE '%str_point%' OR 
                   column_name ILIKE '%end_point%' OR 
                   column_name ILIKE '%tech_point%')
            AND table_name NOT LIKE 'pg_%'
            AND table_name NOT LIKE '_pg_%'
            ORDER BY table_name, column_name;
        """)
        
        if skill_point_tables:
            print("📊 Found skill point related columns:")
            for row in skill_point_tables:
                print(f"  {row['table_name']}.{row['column_name']} ({row['data_type']})")
        else:
            print("❌ No skill point balance columns found!")
        
        # 2. Check skill tree node costs (the currency requirements)
        print("\n🏗️  2. SKILL TREE NODE COSTS (Currency Requirements)")
        print("-" * 40)
        
        node_costs = await conn.fetch("""
            SELECT 
                level,
                COUNT(*) as node_count,
                MIN(stat_points_required) as min_stat_req,
                MAX(stat_points_required) as max_stat_req,
                MIN(required_str_points) as min_str_points,
                MAX(required_str_points) as max_str_points,
                MIN(required_end_points) as min_end_points,
                MAX(required_end_points) as max_end_points,
                MIN(required_tech_points) as min_tech_points,
                MAX(required_tech_points) as max_tech_points
            FROM skill_tree_nodes
            GROUP BY level
            ORDER BY level;
        """)
        
        print("💎 Skill point costs by level:")
        for row in node_costs:
            print(f"  Level {row['level']}: {row['node_count']} nodes")
            if row['min_str_points'] > 0 or row['max_str_points'] > 0:
                print(f"    STR skill points: {row['min_str_points']}-{row['max_str_points']}")
            if row['min_end_points'] > 0 or row['max_end_points'] > 0:
                print(f"    END skill points: {row['min_end_points']}-{row['max_end_points']}")
            if row['min_tech_points'] > 0 or row['max_tech_points'] > 0:
                print(f"    TECH skill points: {row['min_tech_points']}-{row['max_tech_points']}")
        
        # 3. Check for ascendant level system
        print("\n🚀 3. ASCENDANT LEVEL SYSTEM")
        print("-" * 40)
        
        # Look for ascendant/level related tables
        ascendant_tables = await conn.fetch("""
            SELECT table_name, column_name, data_type
            FROM information_schema.columns 
            WHERE (column_name ILIKE '%ascendant%' OR 
                   column_name ILIKE '%level%' OR
                   column_name ILIKE '%xp%' OR
                   column_name ILIKE '%experience%')
            AND table_name NOT LIKE 'pg_%'
            AND table_name NOT LIKE '_pg_%'
            AND table_name NOT ILIKE '%skill_tree%'
            ORDER BY table_name, column_name;
        """)
        
        if ascendant_tables:
            print("📈 Found ascendant/level related columns:")
            current_table = None
            for row in ascendant_tables:
                if row['table_name'] != current_table:
                    print(f"\n  📋 {row['table_name']}:")
                    current_table = row['table_name']
                print(f"    • {row['column_name']} ({row['data_type']})")
        else:
            print("❌ No ascendant level system found!")
        
        # 4. Check for stat milestone rewards
        print("\n🎯 4. STAT MILESTONE REWARD SYSTEM")
        print("-" * 40)
        
        # Look for milestone/reward tables
        milestone_tables = await conn.fetch("""
            SELECT table_name, column_name, data_type
            FROM information_schema.columns 
            WHERE (column_name ILIKE '%milestone%' OR 
                   column_name ILIKE '%reward%' OR
                   column_name ILIKE '%achievement%')
            AND table_name NOT LIKE 'pg_%'
            AND table_name NOT LIKE '_pg_%'
            ORDER BY table_name, column_name;
        """)
        
        if milestone_tables:
            print("🏆 Found milestone/reward related columns:")
            current_table = None
            for row in milestone_tables:
                if row['table_name'] != current_table:
                    print(f"\n  📋 {row['table_name']}:")
                    current_table = row['table_name']
                print(f"    • {row['column_name']} ({row['data_type']})")
        else:
            print("❌ No milestone reward system found!")
        
        # 5. Check user stats (the actual STR/END/TECH levels)
        print("\n💪 5. USER STATS (Actual STR/END/TECH Levels)")
        print("-" * 40)
        
        # Look for user stat tables
        user_stat_tables = await conn.fetch("""
            SELECT table_name, column_name, data_type
            FROM information_schema.columns 
            WHERE (column_name ILIKE '%str%' OR 
                   column_name ILIKE '%end%' OR
                   column_name ILIKE '%tech%' OR
                   column_name ILIKE '%strength%' OR
                   column_name ILIKE '%endurance%' OR
                   column_name ILIKE '%technique%')
            AND table_name NOT LIKE 'pg_%'
            AND table_name NOT LIKE '_pg_%'
            AND table_name NOT ILIKE '%skill_tree%'
            AND column_name NOT ILIKE '%required%'
            AND column_name NOT ILIKE '%point%'
            ORDER BY table_name, column_name;
        """)
        
        if user_stat_tables:
            print("💪 Found user stat related columns:")
            current_table = None
            for row in user_stat_tables:
                if row['table_name'] != current_table:
                    print(f"\n  📋 {row['table_name']}:")
                    current_table = row['table_name']
                print(f"    • {row['column_name']} ({row['data_type']})")
        else:
            print("❌ No user stat system found!")
        
        # 6. Check for skill point earning/spending logic
        print("\n⚙️  6. SKILL POINT EARNING/SPENDING LOGIC")
        print("-" * 40)
        
        # Look for any functions or triggers related to skill points
        functions = await conn.fetch("""
            SELECT routine_name, routine_type
            FROM information_schema.routines
            WHERE routine_schema = 'public'
            AND (routine_name ILIKE '%skill%' OR 
                 routine_name ILIKE '%point%' OR
                 routine_name ILIKE '%ascendant%' OR
                 routine_name ILIKE '%milestone%')
            ORDER BY routine_name;
        """)
        
        if functions:
            print("🔧 Found skill point related functions:")
            for row in functions:
                print(f"  • {row['routine_name']} ({row['routine_type']})")
        else:
            print("❌ No skill point logic functions found!")
        
        # 7. Summary and recommendations
        print("\n📋 7. SKILL POINTS SYSTEM ANALYSIS")
        print("-" * 40)
        
        has_skill_point_storage = len([t for t in skill_point_tables if 'skill_point' in t['column_name'].lower()]) > 0
        has_node_costs = len(node_costs) > 0 and any(row['max_str_points'] > 0 for row in node_costs)
        has_ascendant_system = len([t for t in ascendant_tables if 'ascendant' in t['column_name'].lower() or 'level' in t['column_name'].lower()]) > 0
        has_milestone_system = len(milestone_tables) > 0
        has_user_stats = len(user_stat_tables) > 0
        has_logic = len(functions) > 0
        
        print(f"✅ Skill point storage: {'YES' if has_skill_point_storage else 'NO'}")
        print(f"✅ Node costs configured: {'YES' if has_node_costs else 'NO'}")
        print(f"✅ Ascendant level system: {'YES' if has_ascendant_system else 'NO'}")
        print(f"✅ Milestone reward system: {'YES' if has_milestone_system else 'NO'}")
        print(f"✅ User stats system: {'YES' if has_user_stats else 'NO'}")
        print(f"✅ Skill point logic: {'YES' if has_logic else 'NO'}")
        
        print("\n🎯 MISSING COMPONENTS:")
        if not has_skill_point_storage:
            print("❌ User skill point balance storage (STR/END/TECH skill points)")
        if not has_ascendant_system:
            print("❌ Ascendant level up system")
        if not has_milestone_system:
            print("❌ Stat milestone reward system")
        if not has_logic:
            print("❌ Skill point earning/spending logic")
        
        print("\n💡 RECOMMENDATIONS:")
        print("1. Create user skill point balance table")
        print("2. Implement ascendant level up rewards")
        print("3. Implement stat milestone detection")
        print("4. Add skill point deduction on node unlock")
        print("5. Add skill point earning triggers")
        
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(investigate_skill_points_system())