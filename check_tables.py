#!/usr/bin/env python3
"""Check if dungeon tables exist in the database."""

import asyncio
import os
import sys

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.infrastructure.database.session import get_async_session, initialize_database
from sqlalchemy import text

async def check_tables():
    """Check which dungeon tables exist in the database."""
    initialize_database()
    
    async for session in get_async_session():
        result = await session.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name LIKE 'dungeon_%'
            ORDER BY table_name;
        """))
        tables = result.fetchall()
        print('Existing dungeon tables:')
        for table in tables:
            print(f'  - {table[0]}')
        
        if not tables:
            print('No dungeon tables found!')
        break  # Only need one iteration

if __name__ == "__main__":
    asyncio.run(check_tables())