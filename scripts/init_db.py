#!/usr/bin/env python3
"""
Database Initialization Script for GateGrind V2

This script handles the complete database initialization process:
1. Runs Alembic migrations to create V2 schema
2. Seeds the database with initial data
3. Verifies the setup

Usage:
    python scripts/init_db.py [--force] [--seed-only] [--migrate-only]

Options:
    --force: Force re-initialization (drops existing data)
    --seed-only: Only run seeding, skip migrations
    --migrate-only: Only run migrations, skip seeding
"""

import asyncio
import asyncpg
import os
import sys
import argparse
from pathlib import Path
from typing import Optional

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from alembic.config import Config
from alembic import command
from core.config import get_settings
from scripts.seed import seed_data as run_seed_data


class DatabaseInitializer:
    """Handles database initialization for GateGrind V2"""
    
    def __init__(self, force: bool = False):
        self.settings = get_settings()
        self.force = force
        self.db_pool: Optional[asyncpg.Pool] = None
        
    async def connect(self) -> None:
        """Establish database connection pool"""
        try:
            self.db_pool = await asyncpg.create_pool(
                dsn=self.settings.DATABASE_URL,
                min_size=2,
                max_size=5,
                command_timeout=60
            )
            print("✅ Database connection established")
        except Exception as e:
            print(f"❌ Failed to connect to database: {e}")
            raise
            
    async def disconnect(self) -> None:
        """Close database connection pool"""
        if self.db_pool:
            await self.db_pool.close()
            print("✅ Database connection closed")
            
    async def check_database_exists(self) -> bool:
        """Check if database exists and has tables"""
        try:
            async with self.db_pool.acquire() as conn:
                # Check if any V2 tables exist
                result = await conn.fetchval("""
                    SELECT COUNT(*) 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name IN ('ascendants', 'movement_categories', 'movements')
                """)
                return result > 0
        except Exception as e:
            print(f"⚠️  Error checking database: {e}")
            return False
            
    def run_migrations(self) -> None:
        """Run Alembic migrations to create V2 schema"""
        try:
            print("🔄 Running database migrations...")
            
            # Configure Alembic
            alembic_cfg = Config(str(project_root / "alembic.ini"))
            alembic_cfg.set_main_option("sqlalchemy.url", self.settings.DATABASE_URL)
            
            # Run migrations
            command.upgrade(alembic_cfg, "head")
            print("✅ Database migrations completed successfully")
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            raise
            
    async def seed_data(self) -> None:
        """Seed database with initial data"""
        try:
            print("🌱 Seeding database with initial data...")
            await run_seed_data()
            print("✅ Database seeding completed successfully")
        except Exception as e:
            print(f"❌ Seeding failed: {e}")
            raise
            
    async def verify_setup(self) -> bool:
        """Verify database setup is correct"""
        try:
            print("🔍 Verifying database setup...")
            
            async with self.db_pool.acquire() as conn:
                # Check critical tables exist
                tables_to_check = [
                    'ascendants', 'movement_categories', 'movements', 
                    'skill_tree_nodes', 'quests', 'quest_completions'
                ]
                
                for table in tables_to_check:
                    exists = await conn.fetchval("""
                        SELECT EXISTS (
                            SELECT FROM information_schema.tables 
                            WHERE table_schema = 'public' 
                            AND table_name = $1
                        )
                    """, table)
                    
                    if not exists:
                        print(f"❌ Table '{table}' not found")
                        return False
                        
                # Check if we have seed data
                category_count = await conn.fetchval("SELECT COUNT(*) FROM movement_categories")
                movement_count = await conn.fetchval("SELECT COUNT(*) FROM movements")
                node_count = await conn.fetchval("SELECT COUNT(*) FROM skill_tree_nodes")
                
                print(f"📊 Database contains:")
                print(f"   - {category_count} movement categories")
                print(f"   - {movement_count} movements")
                print(f"   - {node_count} skill tree nodes")
                
                if category_count == 0 or movement_count == 0 or node_count == 0:
                    print("⚠️  Database appears to be missing seed data")
                    return False
                    
                print("✅ Database verification passed")
                return True
                
        except Exception as e:
            print(f"❌ Verification failed: {e}")
            return False
            
    async def initialize(self, migrate_only: bool = False, seed_only: bool = False) -> bool:
        """
        Complete database initialization process
        
        Args:
            migrate_only: Only run migrations, skip seeding
            seed_only: Only run seeding, skip migrations
            
        Returns:
            bool: True if initialization successful
        """
        try:
            await self.connect()
            
            # Check current state
            db_exists = await self.check_database_exists()
            
            if db_exists and not self.force and not seed_only:
                print("ℹ️  Database already exists. Use --force to reinitialize")
                if not migrate_only:
                    # Still verify the setup
                    return await self.verify_setup()
                return True
                
            # Run migrations if needed
            if not seed_only:
                if self.force or not db_exists:
                    self.run_migrations()
                else:
                    print("ℹ️  Skipping migrations (database exists)")
                    
            # Run seeding if needed
            if not migrate_only:
                await self.seed_data()
                
            # Verify setup
            if not migrate_only and not seed_only:
                return await self.verify_setup()
                
            return True
            
        except Exception as e:
            print(f"❌ Database initialization failed: {e}")
            return False
        finally:
            await self.disconnect()


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Initialize GateGrind V2 Database")
    parser.add_argument("--force", action="store_true", 
                       help="Force re-initialization (drops existing data)")
    parser.add_argument("--seed-only", action="store_true",
                       help="Only run seeding, skip migrations")
    parser.add_argument("--migrate-only", action="store_true",
                       help="Only run migrations, skip seeding")
    
    args = parser.parse_args()
    
    if args.seed_only and args.migrate_only:
        print("❌ Cannot specify both --seed-only and --migrate-only")
        sys.exit(1)
        
    print("🚀 Starting GateGrind V2 Database Initialization")
    print("=" * 50)
    
    initializer = DatabaseInitializer(force=args.force)
    success = await initializer.initialize(
        migrate_only=args.migrate_only,
        seed_only=args.seed_only
    )
    
    if success:
        print("=" * 50)
        print("🎉 Database initialization completed successfully!")
        print("🔗 Your GateGrind V2 database is ready to use")
        sys.exit(0)
    else:
        print("=" * 50)
        print("💥 Database initialization failed!")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())