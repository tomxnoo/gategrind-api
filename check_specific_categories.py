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

async def check_specific_categories():
    """Check the specific categories shown in the screenshots."""
    
    conn = await get_db_connection()
    
    try:
        print("🔍 Checking specific categories from screenshots...\n")
        
        # Map interface names to likely category names
        categories_to_check = [
            ("Push", ["Push", "Carry"]),  # Push (1/12) - could be Push or Carry
            ("Pull", ["Pull"]),           # Pull (2/12)
            ("Vertical Pulling", ["Vertical Pulling"])  # Vertical Pulling (3/12)
        ]
        
        for interface_name, possible_names in categories_to_check:
            print(f"🎯 Checking '{interface_name}' category:")
            
            for category_name in possible_names:
                # Get category info
                category_info = await conn.fetchrow("""
                    SELECT id, name FROM movement_categories 
                    WHERE name ILIKE $1;
                """, f"%{category_name}%")
                
                if not category_info:
                    print(f"  ❌ Category '{category_name}' not found")
                    continue
                
                category_id = str(category_info['id'])
                actual_name = category_info['name']
                
                print(f"  📊 Found: {actual_name} (ID: {category_id})")
                
                # Get detailed movement distribution
                movements_by_level = await conn.fetch("""
                    SELECT 
                        stn.level,
                        stn.name as node_name,
                        m.name as movement_name,
                        m.xp_per_rep,
                        m.node_id
                    FROM skill_tree_nodes stn
                    LEFT JOIN movements m ON stn.node_id = m.node_id
                    WHERE stn.category_id = $1
                    ORDER BY stn.level, m.name;
                """, category_id)
                
                current_level = None
                for row in movements_by_level:
                    if row['level'] != current_level:
                        current_level = row['level']
                        print(f"    Level {current_level}: {row['node_name']}")
                    
                    if row['movement_name']:
                        print(f"      • {row['movement_name']} (XP: {row['xp_per_rep']}) -> Node: {row['node_id']}")
                    else:
                        print(f"      (no movements)")
                
                print()
        
        # Check what user tables exist
        print("👤 Checking user-related tables...\n")
        
        user_tables = await conn.fetch("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_name ILIKE '%user%'
            ORDER BY table_name;
        """)
        
        print("User-related tables found:")
        for table in user_tables:
            print(f"  - {table['table_name']}")
        
        # Check skill points system implementation
        print("\n💰 Checking skill points system implementation...\n")
        
        # Check skill tree node costs
        node_costs = await conn.fetch("""
            SELECT 
                level,
                stat_points_required,
                required_str_points,
                required_end_points,
                required_tech_points,
                COUNT(*) as node_count
            FROM skill_tree_nodes 
            WHERE stat_points_required IS NOT NULL OR 
                  required_str_points IS NOT NULL OR 
                  required_end_points IS NOT NULL OR 
                  required_tech_points IS NOT NULL
            GROUP BY level, stat_points_required, required_str_points, required_end_points, required_tech_points
            ORDER BY level;
        """)
        
        print(f"🌳 Skill tree node costs:")
        if node_costs:
            for cost in node_costs:
                level = cost['level']
                stat_pts = cost['stat_points_required'] or 0
                str_pts = cost['required_str_points'] or 0
                end_pts = cost['required_end_points'] or 0
                tech_pts = cost['required_tech_points'] or 0
                count = cost['node_count']
                
                print(f"   Level {level}: {count} nodes - Stat: {stat_pts}, STR: {str_pts}, END: {end_pts}, TECH: {tech_pts}")
        else:
            print("   No cost requirements found in skill tree nodes")
        
        # Check if there are any unlocked skills
        unlocked_skills = await conn.fetch("""
            SELECT 
                usp.node_id,
                stn.name,
                stn.level,
                COUNT(*) as unlock_count
            FROM user_skill_progress usp
            JOIN skill_tree_nodes stn ON usp.node_id = stn.node_id
            GROUP BY usp.node_id, stn.name, stn.level
            ORDER BY stn.level, unlock_count DESC
            LIMIT 10;
        """)
        
        print(f"\n🔓 Most unlocked skills:")
        if unlocked_skills:
            for skill in unlocked_skills:
                print(f"   Level {skill['level']}: {skill['name']} - {skill['unlock_count']} unlocks")
        else:
            print("   No skills have been unlocked yet")
        
        # Check the interface mapping issue
        print(f"\n🔍 Investigating interface display issue...")
        
        # Check if there's a caching or interface issue by looking at the actual data
        push_category = await conn.fetchrow("""
            SELECT id, name FROM movement_categories 
            WHERE name = 'Push';
        """)
        
        if push_category:
            print(f"Push category found: ID {push_category['id']}")
            
            # Check movements for Push category
            push_movements = await conn.fetch("""
                SELECT 
                    m.name,
                    m.node_id,
                    stn.level,
                    stn.name as node_name
                FROM movements m
                JOIN skill_tree_nodes stn ON m.node_id = stn.node_id
                WHERE m.category_id = $1
                ORDER BY stn.level, m.name;
            """, str(push_category['id']))
            
            print(f"Push movements distribution:")
            for mov in push_movements:
                print(f"  Level {mov['level']}: {mov['name']} -> {mov['node_name']}")
        
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(check_specific_categories())