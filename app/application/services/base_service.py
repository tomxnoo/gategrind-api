"""
Base service class for the application layer.

This module provides the foundational service infrastructure that all
business logic services inherit from. It follows the hexagonal architecture
pattern and provides common patterns for dependency injection, error handling,
and transaction management.
"""
import logging
from abc import ABC, abstractmethod
from typing import Optional, Any, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine
import urllib.parse

from core.config import get_settings


class BaseService(ABC):
    """
    Base service class that provides common service patterns.
    
    This class implements the Service Layer pattern from Domain-Driven Design
    and provides:
    - Database session management
    - Error handling and logging
    - Transaction boundaries
    - Dependency injection patterns
    """
    
    def __init__(self, session: Optional[AsyncSession] = None):
        """
        Initialize the base service.
        
        Args:
            session: Optional SQLAlchemy async session. If not provided,
                    a new session will be created when needed.
        """
        self._session = session
        self._logger = logging.getLogger(self.__class__.__name__)
        self._settings = get_settings()
    
    @property
    def logger(self) -> logging.Logger:
        """Get the logger instance for this service."""
        return self._logger
    
    async def get_session(self) -> AsyncSession:
        """
        Get or create a database session.
        
        Returns:
            AsyncSession: SQLAlchemy async session
        """
        if self._session is None:
            # Create a new session if one wasn't provided
            engine = await self._get_engine()
            async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
            self._session = async_session()
        
        return self._session
    
    async def _get_engine(self):
        """
        Create and return a database engine.
        
        Returns:
            AsyncEngine: SQLAlchemy async engine
        """
        db_url = self._normalize_db_url(self._settings.DATABASE_URL)
        return create_async_engine(db_url, echo=False)
    
    def _normalize_db_url(self, url: str) -> str:
        """
        Convert sync postgres URLs to asyncpg URLs & strip problematic params.
        
        Args:
            url: Database URL string
            
        Returns:
            str: Normalized database URL for asyncpg
        """
        # Driver swap
        if url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        elif url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+asyncpg://", 1)

        # Strip params asyncpg chokes on (sslmode, channel_binding, etc.)
        parsed = urllib.parse.urlsplit(url)
        if parsed.query:
            q = urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
            incompatible_params = ["sslmode", "channel_binding", "sslcert", "sslkey", "sslrootcert"]
            filtered = [(k, v) for (k, v) in q if k.lower() not in incompatible_params]
            new_query = urllib.parse.urlencode(filtered)
            url = urllib.parse.urlunsplit(parsed._replace(query=new_query))
        return url
    
    async def execute_in_transaction(self, operation):
        """
        Execute an operation within a database transaction.
        
        Args:
            operation: Async callable that performs database operations
            
        Returns:
            Any: Result of the operation
            
        Raises:
            Exception: Any exception raised during the operation
        """
        session = await self.get_session()
        
        try:
            async with session.begin():
                result = await operation(session)
                return result
        except Exception as e:
            self._logger.error(f"Transaction failed in {self.__class__.__name__}: {e}")
            raise
    
    async def close_session(self):
        """Close the database session if it exists."""
        if self._session:
            await self._session.close()
            self._session = None
    
    def handle_service_error(self, error: Exception, context: str = "") -> None:
        """
        Handle and log service errors consistently.
        
        Args:
            error: The exception that occurred
            context: Additional context about where the error occurred
        """
        error_msg = f"Service error in {self.__class__.__name__}"
        if context:
            error_msg += f" ({context})"
        error_msg += f": {str(error)}"
        
        self._logger.error(error_msg, exc_info=True)
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check for this service.
        
        Returns:
            Dict[str, Any]: Health check results
        """
        pass