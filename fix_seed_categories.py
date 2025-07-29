#!/usr/bin/env python3
"""
Fix the seeding script to work with the existing database schema.
The database uses bigint IDs, not string IDs for categories.
"""

import asyncio
import os
import sys
from urllib.parse import urlparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

async def seed_with_proper_schema():
    """Seed the database using the correct schema with numeric IDs."""
    try:
        import asyncpg
    except ImportError:
        print("ERROR: asyncpg library not available")
        return False
    
    try:
        # Get database URL
        db_url = os.getenv('DATABASE_URL')
        if not db_url:
            print("ERROR: DATABASE_URL environment variable not set")
            return False
        
        print("Connecting to database...")
        
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
        
        print("Connected successfully!")
        
        # First, clear existing data to start fresh
        print("\nClearing existing data...")
        await conn.execute("DELETE FROM movements;")
        await conn.execute("DELETE FROM skill_tree_nodes;")
        await conn.execute("DELETE FROM movement_categories WHERE id > 17;")  # Keep the first 8 categories we created
        
        print("Existing data cleared.")
        
        # Get the comprehensive category list from the seed script
        from scripts.seed import generate_movement_categories_from_unified_library
        v2_categories = generate_movement_categories_from_unified_library()
        
        print(f"\nSeeding {len(v2_categories)} movement categories...")
        
        category_id_map = {}
        
        for cat in v2_categories:
            try:
                # Check if category already exists by name
                existing_id = await conn.fetchval("""
                    SELECT id FROM movement_categories WHERE name = $1;
                """, cat["name"])
                
                if existing_id:
                    category_id_map[cat["id"]] = existing_id
                    print(f"  ✓ Found existing category: {cat['name']} (ID: {existing_id})")
                else:
                    # Insert new category with auto-generated numeric ID
                    new_id = await conn.fetchval("""
                        INSERT INTO movement_categories (category_id, name, primary_stat, created_at, updated_at)
                        VALUES ($1, $2, $3, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                        RETURNING id;
                    """, cat["id"], cat["name"], cat["primary_stat"])
                    
                    category_id_map[cat["id"]] = new_id
                    print(f"  + Added category: {cat['name']} (ID: {new_id}, category_id: {cat['id']})")
                    
            except Exception as e:
                print(f"  ! Error with category {cat['name']}: {e}")
        
        # Now seed skill tree nodes
        print("\nSeeding skill tree nodes...")
        
        from scripts.seed import generate_skill_tree_from_unified_library
        skill_tree = generate_skill_tree_from_unified_library()
        
        node_count = 0
        for category_string_id, nodes in skill_tree.items():
            if category_string_id not in category_id_map:
                print(f"  ! Skipping nodes for missing category: {category_string_id}")
                continue
                
            category_numeric_id = category_id_map[category_string_id]
            
            for node in nodes:
                try:
                    # Check if node already exists
                    existing_node = await conn.fetchval("""
                        SELECT id FROM skill_tree_nodes 
                        WHERE category_id = $1 AND level = $2;
                    """, category_numeric_id, node["level"])
                    
                    if not existing_node:
                        # Insert node with proper requirements
                        node_id = await conn.fetchval("""
                            INSERT INTO skill_tree_nodes (
                                category_id, level, name, description,
                                required_ascendant_level, required_str_points, 
                                required_end_points, required_tech_points,
                                created_at, updated_at
                            )
                            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                            RETURNING id;
                        """, 
                            category_numeric_id,
                            node["level"],
                            node["name"],
                            f"Master the {node['name']} techniques",
                            node["level"] * 5,  # Ascendant level requirement
                            node["level"],      # STR requirement
                            node["level"],      # END requirement
                            node["level"]       # TECH requirement
                        )
                        
                        print(f"  + Added node: {node['name']} (Level {node['level']}) for category ID {category_numeric_id}")
                        node_count += 1
                        
                        # Now add movements for this node
                        for movement_name in node["movements"]:
                            try:
                                # Calculate XP based on level and category
                                xp_per_rep = 0.5 + (node["level"] * 0.3)
                                if "UNILATERAL" in category_string_id or "VERTICAL" in category_string_id:
                                    xp_per_rep *= 1.2
                                
                                await conn.execute("""
                                    INSERT INTO movements (
                                        node_id, name, xp_per_rep, stat_reward_type,
                                        category_id, created_at, updated_at
                                    )
                                    VALUES ($1, $2, $3, $4, $5, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);
                                """, 
                                    str(node_id),  # node_id as string
                                    movement_name,
                                    int(xp_per_rep * 10) / 10,  # Round to 1 decimal
                                    cat["primary_stat"].lower(),
                                    category_numeric_id
                                )
                                
                            except Exception as e:
                                print(f"    ! Error adding movement {movement_name}: {e}")
                    
                except Exception as e:
                    print(f"  ! Error with node {node['name']}: {e}")
        
        await conn.close()
        
        print(f"\n🎉 SUCCESS: Seeding completed!")
        print(f"Added {len(category_id_map)} categories and {node_count} skill tree nodes")
        print("\nNext steps:")
        print("1. Restart your application")
        print("2. Test the Skill Tree panel")
        print("3. You should now see the complete skill tree!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: Seeding failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 70)
    print("SKILL TREE SEEDING WITH PROPER SCHEMA")
    print("=" * 70)
    
    try:
        success = asyncio.run(seed_with_proper_schema())
        if success:
            print("\n✅ Seeding completed successfully!")
        else:
            print("\n❌ Seeding failed - check output above")
    except KeyboardInterrupt:
        print("\n\n⚠️ Seeding interrupted by user")
    except Exception as e:
        print(f"\n\n💥 Unexpected error: {e}")