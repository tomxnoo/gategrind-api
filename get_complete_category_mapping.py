#!/usr/bin/env python3
"""
Script to get the complete category ID to name mapping from the database.
This will help us understand what categories 26-49 represent.
"""

import asyncio
import asyncpg
import os
from urllib.parse import urlparse

async def get_db_connection():
    """Get database connection from environment."""
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        raise ValueError("DATABASE_URL environment variable not set")
    
    # Parse the URL to get connection parameters
    parsed = urlparse(database_url)
    
    return await asyncpg.connect(
        host=parsed.hostname,
        port=parsed.port,
        user=parsed.username,
        password=parsed.password,
        database=parsed.path[1:],  # Remove leading slash
        ssl='require'
    )

async def get_complete_category_mapping():
    """Get all movement categories from the database."""
    print("🔍 Fetching complete category mapping from database...")
    
    conn = await get_db_connection()
    
    try:
        # Get all movement categories
        categories = await conn.fetch("""
            SELECT id, name, primary_stat
            FROM movement_categories 
            ORDER BY id;
        """)
        
        print(f"\nFound {len(categories)} movement categories:")
        print("=" * 60)
        
        category_mapping = {}
        
        for cat in categories:
            category_id = cat['id']
            category_name = cat['name']
            primary_stat = cat['primary_stat']
            
            # Convert name to proper category ID format
            # e.g., "Vertical Pulling" -> "PULL_VERTICAL"
            category_key = category_name.upper().replace(' ', '_').replace('-', '_')
            
            category_mapping[category_id] = category_key
            
            print(f"ID {str(category_id):>2}: {category_name:<30} -> {category_key:<25} ({primary_stat})")
        
        print("\n" + "=" * 60)
        print("Python dictionary format:")
        print("CATEGORY_ID_MAPPING = {")
        for cat_id, cat_key in category_mapping.items():
            print(f"    {cat_id}: \"{cat_key}\",")
        print("}")
        
        # Also check which categories have movements
        print("\n" + "=" * 60)
        print("Categories with movements:")
        
        movement_counts = await conn.fetch("""
            SELECT category_id, COUNT(*) as movement_count
            FROM movements 
            GROUP BY category_id
            ORDER BY category_id;
        """)
        
        for count_data in movement_counts:
            cat_id = count_data['category_id']
            count = count_data['movement_count']
            cat_name = category_mapping.get(cat_id, "UNKNOWN")
            print(f"Category {str(cat_id):>2} ({cat_name:<25}): {count:3d} movements")
        
        return category_mapping
        
    finally:
        await conn.close()

async def main():
    """Main execution function."""
    try:
        mapping = await get_complete_category_mapping()
        print(f"\n✅ Successfully retrieved mapping for {len(mapping)} categories")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())