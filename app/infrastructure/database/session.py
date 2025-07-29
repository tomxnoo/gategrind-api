"""
Database session management for FastAPI dependency injection.

This module provides asynchronous database session management and dependency injection
for FastAPI applications using SQLAlchemy.
"""
import os
import sys
import logging
from typing import AsyncGenerator, Optional
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool, AsyncAdaptedQueuePool
from sqlalchemy.exc import SQLAlchemyError

from app.core.exceptions import DatabaseError

logger = logging.getLogger(__name__)


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
    """Get the database URL from environment variables and normalize for asyncpg."""
    # Default to a test database URL if not specified
    database_url = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:password@localhost/test_db")
    
    # Normalize to asyncpg driver
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    elif not database_url.startswith("postgresql+asyncpg://"):
        # Handle other postgres variants
        for prefix in ["postgres://", "postgresql+psycopg2://", "postgresql+psycopg://"]:
            if database_url.startswith(prefix):
                database_url = database_url.replace(prefix, "postgresql+asyncpg://", 1)
                break
    
    # Remove asyncpg-incompatible parameters
    incompatible_params = ["sslmode", "channel_binding", "sslcert", "sslkey", "sslrootcert"]
    for param in incompatible_params:
        if f"{param}=" in database_url:
            # Remove parameter and its value
            import re
            pattern = f"[?&]{param}=[^&]*"
            database_url = re.sub(pattern, "", database_url)
            # Clean up any double ? or & characters
            database_url = re.sub(r"\?&", "?", database_url)
            database_url = re.sub(r"&&", "&", database_url)
    
    return database_url


def create_engine():
    """Create the async database engine with optimized settings."""
    if is_test_environment():
        return None  # Don't create engine in test environment
    
    database_url = get_database_url()
    
    # Only create engine if we have a proper database URL
    if "postgresql" in database_url:
        # Determine if SSL is required for cloud databases
        connect_args = {
            "command_timeout": 30,
            "server_settings": {
                "jit": "off",  # Disable JIT for faster query startup
                "application_name": "ros-trae"
            }
        }
        
        cloud_providers = ["neon.tech", "amazonaws.com", "supabase", "azure.com"]
        if any(provider in database_url for provider in cloud_providers):
            connect_args["ssl"] = "require"
        
        # Use async-compatible connection pooling in production, NullPool for development
        poolclass = AsyncAdaptedQueuePool if not is_development_mode() else NullPool
        
        # Configure engine parameters based on pool type
        engine_kwargs = {
            "poolclass": poolclass,
            "pool_pre_ping": True,  # Verify connections before use
            "echo": is_development_mode(),  # Enable SQL logging in development
            "connect_args": connect_args
        }
        
        # Only add pool configuration for AsyncAdaptedQueuePool
        if poolclass == AsyncAdaptedQueuePool:
            engine_kwargs.update({
                "pool_size": 10,
                "max_overflow": 20
            })
        
        return create_async_engine(database_url, **engine_kwargs)
    return None


# Global variables for lazy initialization
engine: Optional[object] = None
async_session_factory: Optional[object] = None


def initialize_database():
    """Initialize database engine and session factory if not already done."""
    global engine, async_session_factory
    
    if engine is None and not is_test_environment():
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
        
    Raises:
        DatabaseError: If database connection fails
    """
    if is_test_environment():
        raise RuntimeError("Database sessions should be mocked in test environment")
    
    # Allow database sessions in development mode for testing and development
    # Note: Development mode uses NullPool for simpler connection management
    
    # Initialize database if not already done
    initialize_database()
    
    if not async_session_factory:
        raise DatabaseError(
            "Database session factory not initialized",
            error_code="DB_FACTORY_NOT_INITIALIZED"
        )
    
    session = None
    try:
        session = async_session_factory()
        yield session
        await session.commit()  # Commit any pending transactions
    except SQLAlchemyError as e:
        if session:
            await session.rollback()
        logger.error(f"Database session error: {e}", exc_info=True)
        raise DatabaseError(
            f"Database operation failed: {str(e)}",
            error_code="DB_SESSION_ERROR"
        ) from e
    except Exception as e:
        if session:
            await session.rollback()
        logger.error(f"Unexpected session error: {e}", exc_info=True)
        raise DatabaseError(
            "Unexpected database error occurred",
            error_code="DB_UNEXPECTED_ERROR"
        ) from e
    finally:
        if session:
            await session.close()


# Alias for backward compatibility
get_db = get_async_session