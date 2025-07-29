#!/usr/bin/env python3

import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_movement_distribution():
    """Check how movements are currently distributed across skill tree levels"""
    
    # Get database connection
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not found in environment variables")
        return
    
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        print("🔍 Checking movement distribution across skill tree levels...\n")
        
        # Check movements by skill tree level
        query = """
        SELECT 
            stn.level,
            stn.category_name,
            COUNT(m.id) as movement_count,
            ARRAY_AGG(m.name ORDER BY m.name) as movements
        FROM skill_tree_nodes stn
        LEFT JOIN movements m ON m.skill_tree_level_id = stn.id
        WHERE stn.category_name IN ('Carry', 'Unilateral Pushing')
        GROUP BY stn.level, stn.category_name
        ORDER BY stn.category_name, stn.level;
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        current_category = None
        for level, category_name, count, movements in results:
            if category_name != current_category:
                if current_category is not None:
                    print()
                print(f"📊 {category_name}:")
                current_category = category_name
            
            print(f"  Level {level}: {count} movements")
            if movements and movements[0] is not None:
                for movement in movements[:3]:  # Show first 3
                    print(f"    - {movement}")
                if len(movements) > 3:
                    print(f"    ... and {len(movements) - 3} more")
            else:
                print(f"    (no movements)")
        
        print("\n" + "="*50)
        
        # Check total movements per category
        query2 = """
        SELECT 
            c.name as category_name,
            COUNT(m.id) as total_movements,
            COUNT(CASE WHEN stn.level = 1 THEN 1 END) as level_1_count,
            COUNT(CASE WHEN stn.level > 1 THEN 1 END) as higher_level_count
        FROM categories c
        LEFT JOIN movements m ON m.category_id = c.id
        LEFT JOIN skill_tree_nodes stn ON m.skill_tree_level_id = stn.id
        WHERE c.name IN ('Carry', 'Unilateral Pushing')
        GROUP BY c.name
        ORDER BY c.name;
        """
        
        cursor.execute(query2)
        results2 = cursor.fetchall()
        
        print("📈 Movement Distribution Summary:")
        for category, total, level1, higher in results2:
            print(f"  {category}: {total} total | {level1} in Level 1 | {higher} in Levels 2-5")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error checking movement distribution: {e}")

if __name__ == "__main__":
    check_movement_distribution()