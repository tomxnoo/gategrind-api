#!/usr/bin/env python3
"""
Redistribute movements across all 5 skill levels based on XP values and difficulty.
Currently all movements are linked to level 1, but they should be distributed across levels 1-5.
"""

import asyncio
import os
from urllib.parse import urlparse
import asyncpg

async def redistribute_movements():
    """Redistribute movements across skill levels based on XP values."""
    try:
        # Database connection
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            print("❌ DATABASE_URL environment variable not set")
            return False
        
        # Parse the URL to get connection parameters
        parsed = urlparse(database_url)
        
        conn = await asyncpg.connect(
            host=parsed.hostname,
            port=parsed.port or 5432,
            user=parsed.username,
            password=parsed.password,
            database=parsed.path[1:] if parsed.path else None
        )
        
        print("🔗 Connected to database")
        
        # Get all movements with their current node assignments and XP values
        movements = await conn.fetch("""
            SELECT id, name, category_id, xp_per_rep, node_id
            FROM movements 
            WHERE node_id IS NOT NULL
            ORDER BY category_id, xp_per_rep;
        """)
        
        print(f"📊 Found {len(movements)} movements to redistribute")
        
        # Group movements by category
        movements_by_category = {}
        for movement in movements:
            cat_id = movement['category_id']
            if cat_id not in movements_by_category:
                movements_by_category[cat_id] = []
            movements_by_category[cat_id].append(movement)
        
        print(f"📂 Movements grouped into {len(movements_by_category)} categories")
        
        # Redistribute movements for each category
        total_redistributed = 0
        
        for category_id, cat_movements in movements_by_category.items():
            print(f"\n🔄 Processing category {category_id} ({len(cat_movements)} movements)")
            
            # Sort movements by XP value (difficulty)
            sorted_movements = sorted(cat_movements, key=lambda x: x['xp_per_rep'])
            
            # Distribute movements across 5 levels based on XP percentiles
            num_movements = len(sorted_movements)
            movements_per_level = max(1, num_movements // 5)  # At least 1 per level
            
            level_assignments = []
            
            # Level 1: Lowest XP (0-20th percentile) - Foundation
            level1_end = max(1, num_movements // 5)
            level_assignments.extend([(mov, 1) for mov in sorted_movements[:level1_end]])
            
            # Level 2: Low-medium XP (20-40th percentile) - Development  
            level2_start = level1_end
            level2_end = max(level2_start + 1, (num_movements * 2) // 5)
            level_assignments.extend([(mov, 2) for mov in sorted_movements[level2_start:level2_end]])
            
            # Level 3: Medium XP (40-60th percentile) - Proficiency
            level3_start = level2_end
            level3_end = max(level3_start + 1, (num_movements * 3) // 5)
            level_assignments.extend([(mov, 3) for mov in sorted_movements[level3_start:level3_end]])
            
            # Level 4: High XP (60-80th percentile) - Mastery
            level4_start = level3_end
            level4_end = max(level4_start + 1, (num_movements * 4) // 5)
            level_assignments.extend([(mov, 4) for mov in sorted_movements[level4_start:level4_end]])
            
            # Level 5: Highest XP (80-100th percentile) - Transcendence
            level5_start = level4_end
            level_assignments.extend([(mov, 5) for mov in sorted_movements[level5_start:]])
            
            # Update movements with new node assignments
            for movement, level in level_assignments:
                new_node_id = f"cat_{category_id}_level_{level}"
                
                await conn.execute("""
                    UPDATE movements 
                    SET node_id = $1 
                    WHERE id = $2;
                """, new_node_id, movement['id'])
                
                total_redistributed += 1
            
            # Show distribution for this category
            level_counts = {}
            for _, level in level_assignments:
                level_counts[level] = level_counts.get(level, 0) + 1
            
            print(f"  ✅ Redistributed {len(level_assignments)} movements:")
            for level in range(1, 6):
                count = level_counts.get(level, 0)
                print(f"    Level {level}: {count} movements")
        
        print(f"\n🎉 Successfully redistributed {total_redistributed} movements across all skill levels!")
        
        # Verify the redistribution
        print("\n📊 Verification - Movements per level:")
        level_stats = await conn.fetch("""
            SELECT 
                SUBSTRING(node_id FROM 'level_([0-9]+)') as level,
                COUNT(*) as movement_count
            FROM movements 
            WHERE node_id IS NOT NULL
            GROUP BY SUBSTRING(node_id FROM 'level_([0-9]+)')
            ORDER BY level;
        """)
        
        for stat in level_stats:
            print(f"  Level {stat['level']}: {stat['movement_count']} movements")
        
        # Show sample movements for each level
        print("\n📋 Sample movements per level:")
        for level in range(1, 6):
            sample_movements = await conn.fetch("""
                SELECT name, xp_per_rep, category_id
                FROM movements 
                WHERE node_id LIKE $1
                ORDER BY xp_per_rep
                LIMIT 3;
            """, f"%_level_{level}")
            
            if sample_movements:
                print(f"  Level {level}:")
                for mov in sample_movements:
                    print(f"    - {mov['name']} ({mov['xp_per_rep']} XP/rep)")
        
        await conn.close()
        return True
        
    except Exception as e:
        print(f"\n❌ Error redistributing movements: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 80)
    print("MOVEMENT REDISTRIBUTION ACROSS SKILL LEVELS")
    print("=" * 80)
    print()
    print("This will redistribute movements across all 5 skill levels based on XP values:")
    print("• Level 1 (Foundation): Lowest XP movements (0-0.5 XP/rep)")
    print("• Level 2 (Development): Low-medium XP movements (0.5-1.5 XP/rep)")
    print("• Level 3 (Proficiency): Medium XP movements (1.5-3.0 XP/rep)")
    print("• Level 4 (Mastery): High XP movements (3.0-5.0 XP/rep)")
    print("• Level 5 (Transcendence): Highest XP movements (5.0+ XP/rep)")
    print()
    
    try:
        success = asyncio.run(redistribute_movements())
        if success:
            print("\n✅ Redistribution completed successfully!")
            print("\nNext steps:")
            print("1. Restart your application")
            print("2. Test the Skill Tree panel")
            print("3. All levels should now show movements")
        else:
            print("\n❌ Redistribution failed - check output above")
    except KeyboardInterrupt:
        print("\n\n⚠️ Redistribution interrupted by user")
    except Exception as e:
        print(f"\n\n💥 Unexpected error: {e}")