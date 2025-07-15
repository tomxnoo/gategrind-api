
#!/usr/bin/env python3
"""
Simple database migration script for SQL files
"""
import sys
import os
import asyncio
import asyncpg
from pathlib import Path
from dotenv import load_dotenv

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment variables
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

async def run_migration(sql_file_path: Path):
    """Run a single SQL migration file"""
    if not sql_file_path.exists():
        print(f"❌ Migration file not found: {sql_file_path}")
        return False
    
    try:
        # Read the SQL file
        with open(sql_file_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # Connect to database and execute
        conn = await asyncpg.connect(DATABASE_URL)
        try:
            await conn.execute(sql_content)
            print(f"✅ Successfully executed: {sql_file_path.name}")
            return True
        finally:
            await conn.close()
            
    except Exception as e:
        print(f"❌ Error executing {sql_file_path.name}: {e}")
        return False

async def run_all_migrations():
    """Run all SQL migration files in order"""
    print("=== DATABASE MIGRATION RUNNER ===")
    
    if not DATABASE_URL:
        print("❌ DATABASE_URL not found in environment variables")
        return
    
    # Get all SQL files in scripts directory
    scripts_dir = Path(__file__).parent
    sql_files = sorted([f for f in scripts_dir.glob("*.sql") if f.name.startswith("202")])
    
    if not sql_files:
        print("No SQL migration files found")
        return
    
    print(f"Found {len(sql_files)} migration files:")
    for sql_file in sql_files:
        print(f"  - {sql_file.name}")
    print()
    
    # Run each migration
    success_count = 0
    for sql_file in sql_files:
        if await run_migration(sql_file):
            success_count += 1
        else:
            print(f"⚠️  Stopping migrations due to error in {sql_file.name}")
            break
    
    print(f"\n=== MIGRATION SUMMARY ===")
    print(f"Successfully executed: {success_count}/{len(sql_files)} migrations")
    
    if success_count == len(sql_files):
        print("🎉 All migrations completed successfully!")
    else:
        print("⚠️  Some migrations failed. Please check the errors above.")

async def run_specific_migration(filename: str):
    """Run a specific migration file"""
    print(f"=== RUNNING SPECIFIC MIGRATION: {filename} ===")
    
    if not DATABASE_URL:
        print("❌ DATABASE_URL not found in environment variables")
        return
    
    scripts_dir = Path(__file__).parent
    sql_file = scripts_dir / filename
    
    if await run_migration(sql_file):
        print(f"🎉 Migration {filename} completed successfully!")
    else:
        print(f"❌ Migration {filename} failed!")

def main():
    """Main function to handle command line arguments"""
    if len(sys.argv) > 1:
        # Run specific migration
        filename = sys.argv[1]
        if not filename.endswith('.sql'):
            filename += '.sql'
        asyncio.run(run_specific_migration(filename))
    else:
        # Run all migrations
        asyncio.run(run_all_migrations())

if __name__ == "__main__":
    main()
