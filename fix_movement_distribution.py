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

async def fix_movement_distribution():
    """Fix movement distribution across skill tree levels."""
    
    conn = await get_db_connection()
    
    try:
        print("🔧 Fixing movement distribution across skill tree levels...\n")
        
        # Get categories we want to fix (Carry and Unilateral Pushing)
        categories_to_fix = [
            ('10', 'Carry'),
            ('22', 'Unilateral Pushing')
        ]
        
        for category_id, category_name in categories_to_fix:
            print(f"🎯 Processing {category_name} (ID: {category_id})")
            
            # Get all movements for this category
            movements = await conn.fetch("""
                SELECT id, name, xp_per_rep, node_id
                FROM movements 
                WHERE category_id = $1 AND xp_per_rep IS NOT NULL
                ORDER BY xp_per_rep;
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
            
            # Distribute movements across 5 levels based on XP
            total_movements = len(movements)
            movements_per_level = total_movements // 5
            remainder = total_movements % 5
            
            start_idx = 0
            total_updated = 0
            
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
                total_updated += updated_count
                
                xp_range = f"{level_movements[0]['xp_per_rep']:.1f}-{level_movements[-1]['xp_per_rep']:.1f}"
                print(f"    Level {level}: {updated_count} movements (XP: {xp_range})")
                
                # Show sample movements
                for movement in level_movements[:2]:  # Show first 2
                    print(f"      • {movement['name']} (XP: {movement['xp_per_rep']})")
                if len(level_movements) > 2:
                    print(f"      ... and {len(level_movements) - 2} more")
                
                start_idx = end_idx
            
            print(f"  ✅ Updated {total_updated} movements for {category_name}\n")
        
        # Verify the fix
        print("🔍 Verifying the fix...")
        
        for category_id, category_name in categories_to_fix:
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
        
        print("\n🎉 Movement distribution fix completed!")
        
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(fix_movement_distribution())