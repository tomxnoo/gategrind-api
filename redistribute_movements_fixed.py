#!/usr/bin/env python3
"""
Fixed Movement Redistribution Script

This script properly redistributes movements across skill tree levels by:
1. Mapping numeric category IDs to proper category names
2. Creating correct skill tree node IDs (e.g., "pull_vertical_1")
3. Ensuring skill tree nodes exist before assigning movements
4. Redistributing movements based on XP per repetition across 5 levels

Author: James (Enhanced Dev Agent)
Date: 2024-12-19
"""

import asyncio
import asyncpg
import os
from typing import Dict, List, Tuple, Optional
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database connection
async def get_db_connection():
    """Get database connection using environment variables."""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        # Try alternative environment variable names
        database_url = os.getenv("DB_URL") or os.getenv("POSTGRES_URL")
        if not database_url:
            # Use default for local development
            database_url = "postgresql://user:password@localhost/ros_db"
            print(f"⚠️  No DATABASE_URL found, using default: {database_url}")
    
    try:
        conn = await asyncpg.connect(database_url)
        print("✅ Connected to database successfully")
        return conn
    except Exception as e:
        print(f"❌ Failed to connect to database: {e}")
        raise

# Complete mapping from numeric category IDs to category names (from database)
CATEGORY_ID_MAPPING = {
    10: "PUSH",
    11: "PULL",
    12: "SQUAT",
    13: "HINGE",
    14: "CARRY",
    15: "CORE",
    16: "CARDIO",
    17: "FLEXIBILITY",
    18: "VERTICAL_PULLING",
    19: "HORIZONTAL_PULLING",
    20: "UNILATERAL_PULLING",
    21: "HORIZONTAL_PUSHING",
    22: "UNILATERAL_PUSHING",
    23: "DYNAMIC_POWER_(UPPER)",
    24: "VERTICAL_PUSHING",
    25: "ISOMETRIC_HOLDS_(UPPER)",
    26: "BILATERAL_SQUATS",
    27: "UNILATERAL_SQUATS",
    28: "BILATERAL_HINGE",
    29: "UNILATERAL_HINGE",
    30: "PLYOMETRICS_(LOWER)",
    31: "STATIC_CORE",
    32: "DYNAMIC_CORE",
    33: "ROTATIONAL_CORE",
    34: "MOBILITY_FLOW",
    35: "SHOULDER_STABILITY",
    36: "LOCOMOTION",
    37: "BALANCE",
    38: "COORDINATION",
    39: "PLYOMETRICS_(UPPER)",
    40: "POWER_ENDURANCE",
    42: "GRIP_STRENGTH",
    43: "POSTERIOR_CHAIN",
    44: "RECOVERY",
    45: "STEADY_STATE_CARDIO",
    46: "INTERVAL_TRAINING",
    47: "HANDSTAND_SKILLS",
    48: "BRIDGE_SKILLS",
    49: "FLOW_MOVEMENT",
}

def get_node_id(category_name: str, level: int) -> str:
    """Generate proper node ID from category name and level."""
    return f"{category_name.lower()}_{level}"

async def ensure_skill_tree_nodes_exist(conn: asyncpg.Connection) -> Dict[str, List[str]]:
    """
    Ensure all required skill tree nodes exist for each category.
    Returns mapping of category_name -> [node_ids]
    """
    print("\n🏗️  Ensuring skill tree nodes exist...")
    
    # Get existing categories from the database
    categories = await conn.fetch("""
        SELECT DISTINCT category_id, name, primary_stat 
        FROM movement_categories 
        ORDER BY category_id;
    """)
    
    if not categories:
        print("❌ No movement categories found in database!")
        return {}
    
    print(f"Found {len(categories)} movement categories")
    
    category_nodes = {}
    
    for category in categories:
        category_id = category['category_id'] if isinstance(category['category_id'], str) else str(category['category_id'])
        category_name = category['name']
        primary_stat = category['primary_stat'] or 'STR'
        
        print(f"  Processing category: {category_name} (ID: {category_id})")
        
        # Create nodes for levels 1-5
        node_ids = []
        for level in range(1, 6):
            node_id = get_node_id(category_name.replace(' ', '_').replace('(', '').replace(')', '').upper(), level)
            node_ids.append(node_id)
            
            # Check if node exists
            existing_node = await conn.fetchval("""
                SELECT node_id FROM skill_tree_nodes 
                WHERE node_id = $1;
            """, node_id)
            
            if not existing_node:
                # Create the node
                try:
                    await conn.execute("""
                        INSERT INTO skill_tree_nodes (
                            node_id, category_id, level, name, description,
                            ascendant_level_required, stat_points_required,
                            required_ascendant_level, required_str_points, 
                            required_end_points, required_tech_points,
                            created_at, updated_at
                        ) VALUES (
                            $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11,
                            CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                        );
                    """, 
                    node_id, category_id, level,
                    f"{category_name} Level {level}",
                    f"Level {level} progression for {category_name}",
                    level,  # ascendant_level_required
                    level * 10,  # stat_points_required (basic scaling)
                    level,  # required_ascendant_level
                    level * 100,  # required_str_points (basic scaling)
                    level * 50,   # required_end_points
                    level * 75    # required_tech_points
                    )
                    print(f"    ✅ Created node: {node_id}")
                except Exception as e:
                    print(f"    ❌ Failed to create node {node_id}: {e}")
            else:
                print(f"    ✓ Node exists: {node_id}")
        
        category_nodes[category_name] = node_ids
    
    return category_nodes

async def redistribute_movements_across_levels(conn: asyncpg.Connection):
    """
    Redistribute movements across skill tree levels based on XP per repetition.
    """
    print("\n📊 Starting movement redistribution...")
    
    # DEBUG: Show CATEGORY_ID_MAPPING contents
    print(f"DEBUG: CATEGORY_ID_MAPPING has {len(CATEGORY_ID_MAPPING)} entries:")
    for key, value in list(CATEGORY_ID_MAPPING.items())[:5]:  # Show first 5
        print(f"  {key} ({type(key)}) -> {value}")
    print("  ...")
    
    # Step 1: Ensure skill tree nodes exist
    category_nodes = await ensure_skill_tree_nodes_exist(conn)
    
    if not category_nodes:
        print("❌ No skill tree nodes available for redistribution!")
        return
    
    # Step 2: Get all movements with their XP values
    movements = await conn.fetch("""
        SELECT id, name, category_id, xp_per_rep, node_id
        FROM movements 
        WHERE xp_per_rep IS NOT NULL 
        AND xp_per_rep > 0
        ORDER BY category_id, xp_per_rep;
    """)
    
    if not movements:
        print("❌ No movements found with XP values!")
        return
    
    print(f"Found {len(movements)} movements to redistribute")
    
    # Step 3: Group movements by category and redistribute
    movements_by_category = {}
    for movement in movements:
        category_id = movement['category_id']
        
        # DEBUG: Print category ID type and value
        print(f"DEBUG: Processing movement '{movement['name']}' with category_id: {category_id} (type: {type(category_id)})")
        
        # Convert category_id to integer for lookup
        try:
            if isinstance(category_id, str):
                category_id_int = int(category_id)
            else:
                category_id_int = category_id
        except (ValueError, TypeError):
            print(f"⚠️  Invalid category ID format: {category_id} for movement: {movement['name']}")
            continue
        
        # Look up category name using integer key
        category_name = CATEGORY_ID_MAPPING.get(category_id_int)
        if not category_name:
            print(f"⚠️  Unknown category ID: {category_id_int} for movement: {movement['name']}")
            continue
        
        if category_name not in movements_by_category:
            movements_by_category[category_name] = []
        movements_by_category[category_name].append(movement)
    
    print(f"Grouped movements into {len(movements_by_category)} categories")
    
    # Step 4: Redistribute each category
    total_updated = 0
    
    for category_name, category_movements in movements_by_category.items():
        if category_name not in category_nodes:
            print(f"⚠️  No skill tree nodes found for category: {category_name}")
            continue
        
        print(f"\n📈 Redistributing {len(category_movements)} movements in {category_name}")
        
        # Sort movements by XP (ascending)
        category_movements.sort(key=lambda m: m['xp_per_rep'])
        
        # Calculate XP percentiles for 5 levels
        total_movements = len(category_movements)
        movements_per_level = total_movements // 5
        remainder = total_movements % 5
        
        # Distribute movements across levels
        level_assignments = []
        start_idx = 0
        
        for level in range(1, 6):
            # Add extra movement to earlier levels if there's remainder
            level_size = movements_per_level + (1 if level <= remainder else 0)
            end_idx = start_idx + level_size
            
            level_movements = category_movements[start_idx:end_idx]
            node_id = category_nodes[category_name][level - 1]  # level-1 for 0-based indexing
            
            level_assignments.append((level, node_id, level_movements))
            start_idx = end_idx
        
        # Update movements in database
        for level, node_id, level_movements in level_assignments:
            if not level_movements:
                continue
                
            movement_ids = [m['id'] for m in level_movements]
            xp_range = f"{level_movements[0]['xp_per_rep']:.1f}-{level_movements[-1]['xp_per_rep']:.1f}"
            
            print(f"  Level {level} ({node_id}): {len(level_movements)} movements (XP: {xp_range})")
            
            # Update movements to point to this node
            try:
                result = await conn.execute("""
                    UPDATE movements 
                    SET node_id = $1, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ANY($2);
                """, node_id, movement_ids)
                
                updated_count = int(result.split()[-1])  # Extract count from "UPDATE N"
                total_updated += updated_count
                print(f"    ✅ Updated {updated_count} movements")
                
                # Show sample movements
                for i, movement in enumerate(level_movements[:3]):  # Show first 3
                    print(f"      • {movement['name']} (XP: {movement['xp_per_rep']})")
                if len(level_movements) > 3:
                    print(f"      ... and {len(level_movements) - 3} more")
                    
            except Exception as e:
                print(f"    ❌ Failed to update movements for level {level}: {e}")
    
    print(f"\n🎉 Redistribution complete! Updated {total_updated} movements across skill tree levels")
    
    # Step 5: Verification
    await verify_redistribution(conn)

async def verify_redistribution(conn: asyncpg.Connection):
    """Verify the redistribution was successful."""
    print("\n🔍 Verifying redistribution...")
    
    # Check movements per level
    level_stats = await conn.fetch("""
        SELECT 
            stn.level,
            stn.category_id,
            COUNT(m.id) as movement_count,
            MIN(m.xp_per_rep) as min_xp,
            MAX(m.xp_per_rep) as max_xp,
            AVG(m.xp_per_rep) as avg_xp
        FROM skill_tree_nodes stn
        LEFT JOIN movements m ON stn.node_id = m.node_id
        WHERE m.id IS NOT NULL
        GROUP BY stn.level, stn.category_id
        ORDER BY stn.category_id, stn.level;
    """)
    
    print("\nMovements per level by category:")
    print("-" * 80)
    current_category = None
    
    for stat in level_stats:
        if stat['category_id'] != current_category:
            current_category = stat['category_id']
            print(f"\n{current_category}:")
        
        print(f"  Level {stat['level']}: {stat['movement_count']} movements "
              f"(XP: {stat['min_xp']:.1f}-{stat['max_xp']:.1f}, avg: {stat['avg_xp']:.1f})")
    
    # Check for orphaned movements
    orphaned = await conn.fetchval("""
        SELECT COUNT(*) FROM movements 
        WHERE node_id IS NULL OR node_id NOT IN (
            SELECT node_id FROM skill_tree_nodes
        );
    """)
    
    if orphaned > 0:
        print(f"\n⚠️  Warning: {orphaned} movements are not linked to valid skill tree nodes")
    else:
        print(f"\n✅ All movements are properly linked to skill tree nodes")

async def main():
    """Main execution function."""
    print("🚀 Starting Fixed Movement Redistribution Script")
    print("=" * 60)
    
    try:
        conn = await get_db_connection()
        
        try:
            await redistribute_movements_across_levels(conn)
            print("\n✅ Script completed successfully!")
            
        finally:
            await conn.close()
            print("🔌 Database connection closed")
            
    except Exception as e:
        print(f"\n❌ Script failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())