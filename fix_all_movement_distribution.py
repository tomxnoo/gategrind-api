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

async def fix_all_movement_distribution():
    """Fix movement distribution for ALL categories that need it."""
    
    conn = await get_db_connection()
    
    try:
        print("🔧 Fixing movement distribution for ALL categories...\n")
        
        # Find all categories where movements are clustered in Level 1
        problematic_categories = await conn.fetch("""
            SELECT DISTINCT 
                mc.id as category_id,
                mc.name as category_name,
                COUNT(DISTINCT m.id) as total_movements,
                COUNT(DISTINCT CASE WHEN stn.level = 1 THEN m.id END) as level_1_movements
            FROM movement_categories mc
            JOIN movements m ON mc.id = m.category_id
            JOIN skill_tree_nodes stn ON m.node_id = stn.node_id
            GROUP BY mc.id, mc.name
            HAVING COUNT(DISTINCT m.id) > 1 
            AND COUNT(DISTINCT CASE WHEN stn.level = 1 THEN m.id END) = COUNT(DISTINCT m.id)
            ORDER BY mc.id;
        """)
        
        print(f"🎯 Found {len(problematic_categories)} categories that need fixing:")
        for cat in problematic_categories:
            print(f"  - {cat['category_name']} (ID: {cat['category_id']}) - {cat['total_movements']} movements all in Level 1")
        
        print()
        
        total_categories_fixed = 0
        total_movements_updated = 0
        
        for category in problematic_categories:
            category_id = str(category['category_id'])
            category_name = category['category_name']
            
            print(f"🎯 Processing {category_name} (ID: {category_id})")
            
            # Get all movements for this category
            movements = await conn.fetch("""
                SELECT id, name, xp_per_rep, node_id
                FROM movements 
                WHERE category_id = $1 AND xp_per_rep IS NOT NULL
                ORDER BY xp_per_rep, name;
            """, category_id)
            
            if not movements:
                print(f"  ❌ No movements found for {category_name}")
                continue
            
            print(f"  📊 Found {len(movements)} movements")
            
            # Get skill tree nodes for this category
            nodes = await conn.fetch("""
                SELECT level, node_id, name
                FROM skill_tree_nodes 
                WHERE category_id = $1
                ORDER BY level;
            """, category_id)
            
            if len(nodes) != 5:
                print(f"  ❌ Expected 5 skill tree nodes, found {len(nodes)}")
                continue
            
            print(f"  🏗️  Found {len(nodes)} skill tree levels")
            
            # Distribute movements across 5 levels based on XP and alphabetical order
            total_movements = len(movements)
            movements_per_level = total_movements // 5
            remainder = total_movements % 5
            
            start_idx = 0
            category_updated = 0
            
            for i, node in enumerate(nodes):
                level = node['level']
                node_id = node['node_id']
                
                # Calculate how many movements for this level
                level_size = movements_per_level + (1 if i < remainder else 0)
                end_idx = start_idx + level_size
                
                level_movements = movements[start_idx:end_idx]
                
                if not level_movements:
                    print(f"    Level {level}: 0 movements")
                    continue
                
                # Update movements to point to this level's node
                movement_ids = [m['id'] for m in level_movements]
                
                result = await conn.execute("""
                    UPDATE movements 
                    SET node_id = $1, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ANY($2);
                """, node_id, movement_ids)
                
                updated_count = int(result.split()[-1])
                category_updated += updated_count
                
                if level_movements:
                    xp_range = f"{level_movements[0]['xp_per_rep']:.1f}-{level_movements[-1]['xp_per_rep']:.1f}"
                    print(f"    Level {level}: {updated_count} movements (XP: {xp_range})")
                    
                    # Show sample movements
                    for movement in level_movements[:2]:  # Show first 2
                        print(f"      • {movement['name']} (XP: {movement['xp_per_rep']})")
                    if len(level_movements) > 2:
                        print(f"      ... and {len(level_movements) - 2} more")
                
                start_idx = end_idx
            
            print(f"  ✅ Updated {category_updated} movements for {category_name}\n")
            total_categories_fixed += 1
            total_movements_updated += category_updated
        
        # Verify the fix
        print("🔍 Verifying the fixes...")
        
        for category in problematic_categories:
            category_id = str(category['category_id'])
            category_name = category['category_name']
            
            print(f"\n📊 {category_name} distribution:")
            
            verification = await conn.fetch("""
                SELECT 
                    stn.level,
                    stn.name,
                    COUNT(m.id) as movement_count,
                    MIN(m.xp_per_rep) as min_xp,
                    MAX(m.xp_per_rep) as max_xp
                FROM skill_tree_nodes stn
                LEFT JOIN movements m ON stn.node_id = m.node_id
                WHERE stn.category_id = $1
                GROUP BY stn.level, stn.name
                ORDER BY stn.level;
            """, category_id)
            
            for row in verification:
                if row['movement_count'] > 0:
                    print(f"  Level {row['level']}: {row['movement_count']} movements (XP: {row['min_xp']:.1f}-{row['max_xp']:.1f})")
                else:
                    print(f"  Level {row['level']}: 0 movements")
        
        print(f"\n🎉 Movement distribution fix completed!")
        print(f"  - Fixed {total_categories_fixed} categories")
        print(f"  - Updated {total_movements_updated} movements")
        
        # Check skill points system
        print(f"\n💰 Skill Points System Status:")
        
        # Check if there's a user table with skill points
        user_tables = await conn.fetch("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_name ILIKE '%user%' 
            AND table_name NOT LIKE 'pg_%'
            AND table_name NOT LIKE '_pg_%'
            ORDER BY table_name;
        """)
        
        print(f"User-related tables: {[t['table_name'] for t in user_tables]}")
        
        # Check skill tree node costs
        has_costs = await conn.fetchrow("""
            SELECT COUNT(*) as nodes_with_costs
            FROM skill_tree_nodes 
            WHERE stat_points_required > 0 OR 
                  required_str_points > 0 OR 
                  required_end_points > 0 OR 
                  required_tech_points > 0;
        """)
        
        print(f"Skill tree nodes with costs: {has_costs['nodes_with_costs']}")
        
        if has_costs['nodes_with_costs'] > 0:
            print("✅ Skill points system is configured in skill tree nodes")
            print("❌ But no user table found to track user skill points")
            print("💡 Recommendation: Create a user table or add skill points to existing user system")
        else:
            print("❌ No skill point costs found in skill tree nodes")
        
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(fix_all_movement_distribution())