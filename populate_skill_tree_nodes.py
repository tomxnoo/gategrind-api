#!/usr/bin/env python3
"""
Populate the skill_tree_nodes table with appropriate nodes for each movement category.
Each category will have 5 progression levels (1-5) representing different skill tiers.
"""

import asyncio
import os
from urllib.parse import urlparse
from datetime import datetime

async def populate_skill_tree_nodes():
    """Create skill tree nodes for all movement categories."""
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
        
        # Get all movement categories
        categories = await conn.fetch("""
            SELECT id, name FROM movement_categories ORDER BY id;
        """)
        
        print(f"[INFO] Found {len(categories)} movement categories")
        
        # Check if skill_tree_nodes already exist
        existing_count = await conn.fetchval("SELECT COUNT(*) FROM skill_tree_nodes;")
        if existing_count > 0:
            print(f"[WARNING] {existing_count} skill tree nodes already exist")
            response = input("Do you want to clear and repopulate? (y/N): ")
            if response.lower() != 'y':
                print("[CANCELLED] Operation cancelled by user")
                await conn.close()
                return False
            
            print("[CLEAR] Removing existing skill tree nodes...")
            await conn.execute("DELETE FROM skill_tree_nodes;")
            print(f"  [OK] Removed {existing_count} existing nodes")
        
        # Define level progression names and requirements
        level_data = [
            {
                "level": 1, 
                "name": "Foundation",
                "description": "Basic movements and fundamental skills",
                "required_ascendant_level": 1,
                "required_str_points": 0,
                "required_end_points": 0,
                "required_tech_points": 0
            },
            {
                "level": 2,
                "name": "Development", 
                "description": "Intermediate progressions and skill building",
                "required_ascendant_level": 5,
                "required_str_points": 10,
                "required_end_points": 10,
                "required_tech_points": 10
            },
            {
                "level": 3,
                "name": "Proficiency",
                "description": "Advanced movements and complex patterns",
                "required_ascendant_level": 10,
                "required_str_points": 25,
                "required_end_points": 25,
                "required_tech_points": 25
            },
            {
                "level": 4,
                "name": "Mastery",
                "description": "Expert-level skills and demanding challenges",
                "required_ascendant_level": 20,
                "required_str_points": 50,
                "required_end_points": 50,
                "required_tech_points": 50
            },
            {
                "level": 5,
                "name": "Transcendence",
                "description": "Elite movements and ultimate expressions",
                "required_ascendant_level": 35,
                "required_str_points": 100,
                "required_end_points": 100,
                "required_tech_points": 100
            }
        ]
        
        print(f"\n[CREATE] Creating skill tree nodes...")
        total_nodes = 0
        
        for category in categories:
            category_id = category['id']  # Keep as integer to match foreign key
            category_name = category['name']
            
            print(f"  Creating nodes for '{category_name}' (ID: {category_id})")
            
            for level_info in level_data:
                level = level_info['level']
                node_id = f"cat_{category_id}_level_{level}"
                
                # Check actual column names first (run check script to see the real schema)
                # Based on the error, it seems the column might be named differently
                # Let's first check what the actual column names are
                
                # Get the actual column names from the table
                if not hasattr(populate_skill_tree_nodes, '_columns_checked'):
                    columns = await conn.fetch("""
                        SELECT column_name FROM information_schema.columns 
                        WHERE table_name = 'skill_tree_nodes'
                        ORDER BY ordinal_position;
                    """)
                    col_names = [col['column_name'] for col in columns]
                    print(f"    [DEBUG] Actual columns: {col_names}")
                    populate_skill_tree_nodes._columns_checked = True
                
                # Create the node with both old and new column names for compatibility
                total_stat_points = (level_info['required_str_points'] + 
                                   level_info['required_end_points'] + 
                                   level_info['required_tech_points'])
                
                await conn.execute("""
                    INSERT INTO skill_tree_nodes (
                        node_id, category_id, level, name, description,
                        ascendant_level_required, stat_points_required,
                        required_ascendant_level, required_str_points, 
                        required_end_points, required_tech_points,
                        created_at, updated_at
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13);
                """, 
                    node_id,
                    str(category_id),  # Convert to string to match VARCHAR column
                    level,
                    f"{category_name} - {level_info['name']}",
                    f"{level_info['description']} for {category_name.lower()} movements",
                    level_info['required_ascendant_level'],  # Old column
                    total_stat_points,                       # Old column (sum of all stat points)
                    level_info['required_ascendant_level'],  # New column
                    level_info['required_str_points'],       # New column
                    level_info['required_end_points'],       # New column
                    level_info['required_tech_points'],      # New column
                    datetime.utcnow(),
                    datetime.utcnow()
                )
                
                total_nodes += 1
            
            print(f"    [OK] Created 5 levels for {category_name}")
        
        print(f"\n[SUCCESS] Created {total_nodes} skill tree nodes!")
        
        # Update movements to link to appropriate skill tree nodes (level 1 by default)
        print("\n[LINK] Linking movements to skill tree nodes...")
        
        # First, check movements.node_id column exists and is nullable
        node_id_exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'movements' AND column_name = 'node_id'
            );
        """)
        
        if node_id_exists:
            # Update movements to link to level 1 nodes of their category
            movements_updated = await conn.execute("""
                UPDATE movements 
                SET node_id = 'cat_' || category_id || '_level_1'
                WHERE node_id IS NULL;
            """)
            
            # Extract count (e.g., "UPDATE 167" -> 167)
            count = int(movements_updated.split()[-1]) if movements_updated.startswith('UPDATE') else 0
            print(f"  [OK] Linked {count} movements to level 1 nodes")
        else:
            print("  [SKIP] movements.node_id column doesn't exist - movements not linked")
        
        # Verify the creation
        print("\n[VERIFY] Verifying skill tree nodes...")
        
        final_count = await conn.fetchval("SELECT COUNT(*) FROM skill_tree_nodes;")
        print(f"Total skill tree nodes: {final_count}")
        
        # Show sample nodes
        sample_nodes = await conn.fetch("""
            SELECT node_id, category_id, level, name 
            FROM skill_tree_nodes 
            ORDER BY category_id, level 
            LIMIT 10;
        """)
        
        print("\nSample skill tree nodes:")
        for node in sample_nodes:
            print(f"  {node['node_id']} - Level {node['level']}: {node['name']}")
        
        # Check nodes per category
        nodes_per_category = await conn.fetch("""
            SELECT category_id, COUNT(*) as node_count
            FROM skill_tree_nodes 
            GROUP BY category_id 
            ORDER BY category_id::int
            LIMIT 5;
        """)
        
        print("\nNodes per category (first 5):")
        for cat in nodes_per_category:
            print(f"  Category {cat['category_id']}: {cat['node_count']} nodes")
        
        await conn.close()
        
        print("\n[SUCCESS] Skill tree nodes populated successfully!")
        print("\nNext steps:")
        print("1. Restart your application")
        print("2. Test the Skill Tree panel")
        print("3. The panel should now load with all categories and levels")
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Population failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 80)
    print("SKILL TREE NODES POPULATION")
    print("=" * 80)
    print()
    print("This will create skill tree nodes for all movement categories.")
    print("Each category will get 5 progression levels (Foundation to Transcendence).")
    print()
    print("Estimated nodes to create: 39 categories × 5 levels = 195 nodes")
    print()
    
    try:
        success = asyncio.run(populate_skill_tree_nodes())
        if success:
            print("\n[SUCCESS] Population completed successfully!")
        else:
            print("\n[ERROR] Population failed - check output above")
    except KeyboardInterrupt:
        print("\n\n[WARNING] Population interrupted by user")
    except Exception as e:
        print(f"\n\n[FATAL] Unexpected error: {e}")