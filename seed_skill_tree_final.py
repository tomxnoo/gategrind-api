#!/usr/bin/env python3
"""
Final comprehensive skill tree seeding script.
This handles all the schema quirks we've discovered.
"""

import asyncio
import os
from urllib.parse import urlparse

async def seed_skill_tree_final():
    """Seed skill tree with movements - final working version."""
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
        
        # First check the schema to understand what we're working with
        print("\nChecking table schemas...")
        
        # Check if category_id in skill_tree_nodes is string or int
        node_cat_id_type = await conn.fetchval("""
            SELECT data_type 
            FROM information_schema.columns 
            WHERE table_name = 'skill_tree_nodes' AND column_name = 'category_id';
        """)
        print(f"skill_tree_nodes.category_id type: {node_cat_id_type}")
        
        # Get existing categories
        print("\nFetching existing categories...")
        categories = await conn.fetch("""
            SELECT id, category_id, name, primary_stat 
            FROM movement_categories 
            ORDER BY id;
        """)
        
        print(f"Found {len(categories)} categories")
        
        # For now, let's just add movements to existing categories without skill tree nodes
        # This will at least populate the skill tree panel with movements
        print("\nSeeding movements for existing categories...")
        
        movement_count = 0
        
        # Simple movement data for each category type
        movement_templates = {
            'push': [
                ("Push-up", 1.0),
                ("Diamond Push-up", 1.2),
                ("Wide-Grip Push-up", 1.0),
                ("Decline Push-up", 1.3),
                ("Archer Push-up", 1.5)
            ],
            'pull': [
                ("Pull-up", 1.5),
                ("Chin-up", 1.4),
                ("Wide-Grip Pull-up", 1.6),
                ("Neutral-Grip Pull-up", 1.4),
                ("L-Sit Pull-up", 2.0)
            ],
            'squat': [
                ("Bodyweight Squat", 0.8),
                ("Jump Squat", 1.0),
                ("Pistol Squat", 2.0),
                ("Bulgarian Split Squat", 1.2),
                ("Goblet Squat", 1.0)
            ],
            'hinge': [
                ("Romanian Deadlift", 1.2),
                ("Hip Thrust", 1.0),
                ("Good Morning", 1.0),
                ("Single-Leg Deadlift", 1.5),
                ("Nordic Curl", 2.0)
            ],
            'core': [
                ("Plank", 0.5),
                ("Side Plank", 0.6),
                ("Dead Bug", 0.8),
                ("Bird Dog", 0.7),
                ("Hollow Body Hold", 1.0)
            ],
            'cardio': [
                ("Running", 0.1),
                ("Jumping Jacks", 0.2),
                ("Burpees", 0.5),
                ("Mountain Climbers", 0.3),
                ("High Knees", 0.2)
            ],
            'flexibility': [
                ("Hamstring Stretch", 0.3),
                ("Hip Flexor Stretch", 0.3),
                ("Shoulder Stretch", 0.3),
                ("Calf Stretch", 0.3),
                ("Quad Stretch", 0.3)
            ],
            'carry': [
                ("Farmer's Walk", 1.0),
                ("Suitcase Carry", 1.2),
                ("Overhead Carry", 1.5),
                ("Rack Carry", 1.3),
                ("Waiter's Walk", 1.4)
            ],
            'balance': [
                ("Single-Leg Stand", 0.5),
                ("Tree Pose", 0.6),
                ("Single-Leg Deadlift", 1.2),
                ("Pistol Squat", 2.0),
                ("Balance Board Work", 0.8)
            ],
            'plyometric': [
                ("Box Jump", 1.5),
                ("Depth Jump", 2.0),
                ("Broad Jump", 1.3),
                ("Lateral Jump", 1.2),
                ("Tuck Jump", 1.0)
            ]
        }
        
        # Default movements for categories not in templates
        default_movements = [
            ("Basic Movement", 1.0),
            ("Intermediate Movement", 1.5),
            ("Advanced Movement", 2.0)
        ]
        
        for cat in categories:
            cat_id = cat['id']
            cat_name = cat['name'].lower()
            cat_stat = cat['primary_stat'].lower() if cat['primary_stat'] else 'strength'
            
            # Find appropriate movements based on category name
            movements = None
            for key in movement_templates:
                if key in cat_name:
                    movements = movement_templates[key]
                    break
            
            if not movements:
                movements = default_movements
            
            # Insert movements
            for movement_name, xp_value in movements:
                try:
                    # Adjust movement name to include category context
                    if movement_name in ["Basic Movement", "Intermediate Movement", "Advanced Movement"]:
                        full_name = f"{cat['name']} - {movement_name}"
                    else:
                        full_name = movement_name
                    
                    await conn.execute("""
                        INSERT INTO movements (
                            name, category_id, stat_reward_type, xp_per_rep, 
                            node_id, created_at, updated_at
                        )
                        VALUES ($1, $2, $3, $4, NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);
                    """, full_name, cat_id, cat_stat, xp_value)
                    
                    movement_count += 1
                    
                except Exception as e:
                    if "duplicate key" not in str(e):
                        print(f"  ! Error adding movement {full_name}: {e}")
            
            print(f"  ✓ Added movements for {cat['name']} (ID: {cat_id})")
        
        await conn.close()
        
        print(f"\n🎉 SUCCESS: Added {movement_count} movements!")
        print("\nThe Skill Tree panel should now display:")
        print(f"- {len(categories)} movement categories")
        print(f"- {movement_count} movements distributed across categories")
        print("\nNext steps:")
        print("1. Restart your application")
        print("2. Test the Skill Tree panel")
        print("3. Users can now log movements and gain XP!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: Seeding failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 70)
    print("FINAL SKILL TREE SEEDING - MOVEMENTS ONLY")
    print("=" * 70)
    print()
    print("This script will add movements to all existing categories")
    print("without requiring skill tree nodes, making the system functional.")
    print()
    
    try:
        success = asyncio.run(seed_skill_tree_final())
        if success:
            print("\n✅ Seeding completed successfully!")
        else:
            print("\n❌ Seeding failed - check output above")
    except KeyboardInterrupt:
        print("\n\n⚠️ Seeding interrupted by user")
    except Exception as e:
        print(f"\n\n💥 Unexpected error: {e}")