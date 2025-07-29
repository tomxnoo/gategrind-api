#!/usr/bin/env python3

import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_schema():
    """Check the schema of movements and skill_tree_nodes tables"""
    
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not found")
        return
    
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        print("🔍 Checking table schemas...\n")
        
        # Check movements table schema
        cursor.execute("""
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns 
        WHERE table_name = 'movements'
        ORDER BY ordinal_position;
        """)
        
        print("📋 MOVEMENTS table schema:")
        for row in cursor.fetchall():
            print(f"  {row[0]} | {row[1]} | nullable: {row[2]} | default: {row[3]}")
        
        print("\n" + "="*50 + "\n")
        
        # Check skill_tree_nodes table schema  
        cursor.execute("""
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns 
        WHERE table_name = 'skill_tree_nodes'
        ORDER BY ordinal_position;
        """)
        
        print("📋 SKILL_TREE_NODES table schema:")
        for row in cursor.fetchall():
            print(f"  {row[0]} | {row[1]} | nullable: {row[2]} | default: {row[3]}")
        
        print("\n" + "="*50 + "\n")
        
        # Check if there's a relationship table
        cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_name LIKE '%movement%' OR table_name LIKE '%skill%'
        ORDER BY table_name;
        """)
        
        print("📋 Tables with 'movement' or 'skill' in name:")
        for row in cursor.fetchall():
            print(f"  {row[0]}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_schema()