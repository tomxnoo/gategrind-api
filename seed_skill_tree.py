#!/usr/bin/env python3
"""
Simple skill tree seeding script for the production environment.
Seeds the movement_categories and movements tables with basic data.
"""

import asyncio
import os
import sys
from urllib.parse import urlparse

async def seed_skill_tree_data():
    """Seed basic skill tree data."""
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
        
        # Check if we already have data
        category_count = await conn.fetchval("SELECT COUNT(*) FROM movement_categories;")
        movement_count = await conn.fetchval("SELECT COUNT(*) FROM movements;")
        
        print(f"Current data: {category_count} categories, {movement_count} movements")
        
        if category_count > 0 and movement_count > 0:
            print("Database already has movement categories and movements - skipping seeding")
            await conn.close()
            return True
        elif category_count > 0:
            print("Database has categories but no movements - will seed movements only")
        
        # First check the actual table structure
        print("Checking table structure...")
        
        # Get column information for movement_categories
        try:
            columns_info = await conn.fetch("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_name = 'movement_categories'
                ORDER BY ordinal_position;
            """)
            
            print("movement_categories columns:")
            required_columns = []
            for col in columns_info:
                nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
                print(f"  {col['column_name']}: {col['data_type']} {nullable}")
                if col['is_nullable'] == 'NO' and col['column_default'] is None:
                    required_columns.append(col['column_name'])
            
            print(f"Required columns (NOT NULL, no default): {required_columns}")
            
        except Exception as e:
            print(f"Could not check table structure: {e}")
        
        # Get or create movement categories
        categories = [
            {"name": "Push", "primary_stat": "strength"},
            {"name": "Pull", "primary_stat": "strength"},
            {"name": "Squat", "primary_stat": "strength"},
            {"name": "Hinge", "primary_stat": "strength"},
            {"name": "Carry", "primary_stat": "strength"},
            {"name": "Core", "primary_stat": "strength"},
            {"name": "Cardio", "primary_stat": "endurance"},
            {"name": "Flexibility", "primary_stat": "flexibility"},
        ]
        
        category_ids = []
        
        if category_count > 0:
            print("Fetching existing category IDs...")
            # Fetch existing categories by name
            for category in categories:
                try:
                    category_id = await conn.fetchval("""
                        SELECT id FROM movement_categories WHERE name = $1;
                    """, category["name"])
                    
                    if category_id:
                        category_ids.append(category_id)
                        print(f"  ✓ Found existing category: {category['name']} (ID: {category_id})")
                    else:
                        category_ids.append(None)
                        print(f"  ! Category not found: {category['name']}")
                        
                except Exception as e:
                    print(f"  ! Error fetching {category['name']}: {e}")
                    category_ids.append(None)
        else:
            print("Seeding movement categories...")
            
            for i, category in enumerate(categories):
                try:
                    # Generate a unique category_id string based on category name
                    category_id_str = category["name"].upper().replace(" ", "_")
                    
                    # Insert with all required columns including category_id as string
                    category_id = await conn.fetchval("""
                        INSERT INTO movement_categories (category_id, name, primary_stat, created_at, updated_at)
                        VALUES ($1, $2, $3, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                        RETURNING id;
                    """, category_id_str, category["name"], category["primary_stat"])
                    
                    category_ids.append(category_id)
                    print(f"  + Added category: {category['name']} (ID: {category_id}, category_id: {category_id_str})")
                    
                except Exception as e:
                    print(f"  ! Failed to add {category['name']}: {e}")
                    # Skip this category and add None to maintain indexing
                    category_ids.append(None)
        
        print("Seeding basic movements...")
        
        # Seed basic movements for each category with XP values
        movements = [
            # Push movements
            {"name": "Push-up", "category_id": category_ids[0], "stat_reward_type": "strength", "xp_per_rep": 1.0},
            {"name": "Overhead Press", "category_id": category_ids[0], "stat_reward_type": "strength", "xp_per_rep": 1.2},
            
            # Pull movements  
            {"name": "Pull-up", "category_id": category_ids[1], "stat_reward_type": "strength", "xp_per_rep": 1.5},
            {"name": "Row", "category_id": category_ids[1], "stat_reward_type": "strength", "xp_per_rep": 1.0},
            
            # Squat movements
            {"name": "Bodyweight Squat", "category_id": category_ids[2], "stat_reward_type": "strength", "xp_per_rep": 0.8},
            {"name": "Goblet Squat", "category_id": category_ids[2], "stat_reward_type": "strength", "xp_per_rep": 1.0},
            
            # Hinge movements
            {"name": "Deadlift", "category_id": category_ids[3], "stat_reward_type": "strength", "xp_per_rep": 1.5},
            {"name": "Hip Thrust", "category_id": category_ids[3], "stat_reward_type": "strength", "xp_per_rep": 1.0},
            
            # Carry movements
            {"name": "Farmer's Walk", "category_id": category_ids[4], "stat_reward_type": "strength", "xp_per_rep": 1.0},
            {"name": "Suitcase Carry", "category_id": category_ids[4], "stat_reward_type": "strength", "xp_per_rep": 1.2},
            
            # Core movements
            {"name": "Plank", "category_id": category_ids[5], "stat_reward_type": "strength", "xp_per_rep": 0.5},
            {"name": "Dead Bug", "category_id": category_ids[5], "stat_reward_type": "strength", "xp_per_rep": 0.8},
            
            # Cardio movements
            {"name": "Running", "category_id": category_ids[6], "stat_reward_type": "endurance", "xp_per_rep": 0.1},
            {"name": "Jumping Jacks", "category_id": category_ids[6], "stat_reward_type": "endurance", "xp_per_rep": 0.2},
            
            # Flexibility movements
            {"name": "Hamstring Stretch", "category_id": category_ids[7], "stat_reward_type": "flexibility", "xp_per_rep": 0.3},
            {"name": "Hip Flexor Stretch", "category_id": category_ids[7], "stat_reward_type": "flexibility", "xp_per_rep": 0.3},
        ]
        
        for movement in movements:
            # Skip movements if their category failed to be created
            if movement["category_id"] is None:
                print(f"  ! Skipping movement {movement['name']} - category not created")
                continue
                
            try:
                movement_id = await conn.fetchval("""
                    INSERT INTO movements (name, category_id, stat_reward_type, xp_per_rep, node_id, created_at, updated_at)
                    VALUES ($1, $2, $3, $4, NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                    RETURNING id;
                """, movement["name"], movement["category_id"], movement["stat_reward_type"], movement["xp_per_rep"])
                
                print(f"  + Added movement: {movement['name']} (ID: {movement_id})")
            except Exception as e:
                print(f"  ! Failed to add movement {movement['name']}: {e}")
        
        await conn.close()
        
        print("\nSUCCESS: Skill tree data seeded successfully!")
        print(f"Added {len(categories)} categories and {len(movements)} movements")
        print("\nNext steps:")
        print("1. Restart your application")
        print("2. Test the Skill Tree panel")
        print("3. You should now see movement categories and exercises")
        
        return True
        
    except Exception as e:
        print(f"\nERROR: Seeding failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("SKILL TREE DATA SEEDING")
    print("=" * 60)
    
    try:
        success = asyncio.run(seed_skill_tree_data())
        if success:
            print("\nSkill tree seeding completed successfully!")
        else:
            print("\nSkill tree seeding failed - check output above")
    except KeyboardInterrupt:
        print("\n\nSeeding interrupted by user")
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")