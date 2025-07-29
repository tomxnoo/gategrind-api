#!/usr/bin/env python3

import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_movement_node_links():
    """Check how movements are linked to skill tree nodes"""
    
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not found")
        return
    
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        print("🔍 Checking movement to skill tree node relationships...\n")
        
        # Check movements for Carry and Unilateral Pushing categories
        query = """
        SELECT 
            m.name,
            m.node_id as movement_node_id,
            m.category_id,
            m.xp_per_rep,
            stn.level,
            stn.name as skill_node_name,
            stn.node_id as skill_node_id
        FROM movements m
        LEFT JOIN skill_tree_nodes stn ON m.node_id = stn.node_id
        WHERE m.category_id IN ('10', '22')  -- Carry and Unilateral Pushing
        ORDER BY m.category_id, m.name;
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        print("📊 Movement to Skill Tree Node Links:")
        current_category = None
        for name, mov_node_id, cat_id, xp, level, skill_node_name, skill_node_id in results:
            category_name = "Carry" if cat_id == "10" else "Unilateral Pushing"
            if category_name != current_category:
                if current_category is not None:
                    print()
                print(f"🏷️  {category_name} (Category ID: {cat_id}):")
                current_category = category_name
            
            if level:
                print(f"  ✅ {name} (XP: {xp}) -> Level {level} | Node: {mov_node_id}")
            else:
                print(f"  ❌ {name} (XP: {xp}) -> NO LINK | Node: {mov_node_id}")
        
        print("\n" + "="*60 + "\n")
        
        # Check skill tree nodes for these categories
        query2 = """
        SELECT 
            stn.category_id,
            stn.level,
            stn.node_id,
            stn.name,
            COUNT(m.id) as linked_movements
        FROM skill_tree_nodes stn
        LEFT JOIN movements m ON stn.node_id = m.node_id
        WHERE stn.category_id IN ('10', '22')
        GROUP BY stn.category_id, stn.level, stn.node_id, stn.name
        ORDER BY stn.category_id, stn.level;
        """
        
        cursor.execute(query2)
        results2 = cursor.fetchall()
        
        print("🎯 Skill Tree Nodes and Their Linked Movements:")
        current_category = None
        for cat_id, level, node_id, name, count in results2:
            category_name = "Carry" if cat_id == "10" else "Unilateral Pushing"
            if category_name != current_category:
                if current_category is not None:
                    print()
                print(f"🏷️  {category_name} (Category ID: {cat_id}):")
                current_category = category_name
            
            print(f"  Level {level}: {name} | Node: {node_id} | {count} movements linked")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_movement_node_links()