"""
Database session management for FastAPI dependency injection.

This module provides asynchronous database session management and dependency injection
for FastAPI applications using SQLAlchemy.
"""
import os
import sys
from typing import AsyncGenerator, Optional
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool


def is_test_environment() -> bool:
    """Check if we're running in a test environment."""
    return (
        "pytest" in sys.modules or
        os.getenv("PYTEST_CURRENT_TEST") is not None or
        "test" in sys.argv[0].lower()
    )


def is_development_mode() -> bool:
    """Check if we're running in development mode."""
    return os.getenv("DEVELOPMENT_MODE", "false").lower() == "true"


def get_database_url() -> str:
    """Get the database URL from environment variables."""
    # Default to a test database URL if not specified
    return os.getenv("DATABASE_URL", "postgresql+asyncpg://user:password@localhost/test_db")


def create_engine():
    """Create the async database engine."""
    if is_test_environment() or is_development_mode():
        return None  # Don't create engine in test or development environment
    
    database_url = get_database_url()
    
    # Only create engine if we have a proper database URL
    if "postgresql" in database_url:
        return create_async_engine(
            database_url,
            poolclass=NullPool,  # Disable connection pooling for testing
            echo=False
        )
    return None


# Global variables for lazy initialization
engine: Optional[object] = None
async_session_factory: Optional[object] = None


def initialize_database():
    """Initialize database engine and session factory if not already done."""
    global engine, async_session_factory
    
    if engine is None and not is_test_environment() and not is_development_mode():
        engine = create_engine()
        if engine:
            async_session_factory = async_sessionmaker(
                engine,
                class_=AsyncSession,
                expire_on_commit=False
            )


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency function to provide async database sessions for FastAPI.
    
    This function creates a new database session for each request and ensures
    it's properly closed after use.
    
    Yields:
        AsyncSession: Database session for the request
    """
    if is_test_environment():
        raise RuntimeError("Database sessions should be mocked in test environment")
    
    if is_development_mode():
        raise RuntimeError("Database sessions are disabled in development mode")
    
    # Initialize database if not already done
    initialize_database()
    
    if not async_session_factory:
        raise RuntimeError("Database session factory not initialized")
    
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()