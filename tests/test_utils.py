"""
Enhanced testing utilities for the RoS application.

This module provides comprehensive testing support including:
- Database fixtures with proper isolation
- Mock data factories
- Performance testing helpers
- API testing utilities
"""
import asyncio
import pytest
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, AsyncGenerator
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
import factory

from app.infrastructure.database.models.v2 import (
    Ascendant, DungeonSession, DungeonTrial, DungeonProgress
)


class AsyncFactory(factory.Factory):
    """Base factory for async model creation."""
    
    @classmethod
    async def create_async(cls, **kwargs):
        """Create instance asynchronously."""
        return cls.build(**kwargs)
    
    @classmethod
    async def create_batch_async(cls, size: int, **kwargs):
        """Create multiple instances asynchronously."""
        return [await cls.create_async(**kwargs) for _ in range(size)]


class AscendantFactory(AsyncFactory):
    """Factory for creating Ascendant test instances."""
    
    class Meta:
        model = Ascendant
    
    discord_user_id = factory.Sequence(lambda n: f"user_{n}")
    level = factory.Faker('random_int', min=1, max=100)
    xp = factory.LazyAttribute(lambda obj: obj.level * 1000)
    aura = factory.Faker('random_int', min=100, max=10000)
    shadow_essence = factory.Faker('random_int', min=0, max=1000)
    skill_points = factory.Faker('random_int', min=0, max=50)
    last_login = factory.LazyFunction(lambda: datetime.now(timezone.utc))


class DungeonSessionFactory(AsyncFactory):
    """Factory for creating DungeonSession test instances."""
    
    class Meta:
        model = DungeonSession
    
    ascendant_id = factory.SubFactory(AscendantFactory)
    level = factory.Faker('random_int', min=1, max=10)
    status = "active"
    created_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))
    expires_at = factory.LazyAttribute(
        lambda obj: obj.created_at + timedelta(hours=1)
    )


class DungeonTrialFactory(AsyncFactory):
    """Factory for creating DungeonTrial test instances."""
    
    class Meta:
        model = DungeonTrial
    
    session_id = factory.SubFactory(DungeonSessionFactory)
    trial_number = factory.Sequence(lambda n: n + 1)
    movement_id = factory.Faker('random_int', min=1, max=100)
    target_reps = factory.Faker('random_int', min=10, max=50)
    completed_reps = 0
    status = "active"


class TestDataBuilder:
    """Builder pattern for creating complex test data scenarios."""
    
    def __init__(self):
        self.data = {}
    
    async def with_ascendant(
        self,
        discord_user_id: str = "test_user",
        level: int = 10,
        **kwargs
    ) -> 'TestDataBuilder':
        """Add an ascendant to the test data."""
        ascendant = await AscendantFactory.create_async(
            discord_user_id=discord_user_id,
            level=level,
            **kwargs
        )
        self.data['ascendant'] = ascendant
        return self
    
    async def with_dungeon_session(
        self,
        level: int = 1,
        status: str = "active",
        **kwargs
    ) -> 'TestDataBuilder':
        """Add a dungeon session to the test data."""
        if 'ascendant' not in self.data:
            await self.with_ascendant()
        
        session = await DungeonSessionFactory.create_async(
            ascendant_id=self.data['ascendant'].discord_user_id,
            level=level,
            status=status,
            **kwargs
        )
        self.data['dungeon_session'] = session
        return self
    
    async def with_trials(
        self,
        count: int = 3,
        **kwargs
    ) -> 'TestDataBuilder':
        """Add trials to the dungeon session."""
        if 'dungeon_session' not in self.data:
            await self.with_dungeon_session()
        
        trials = await DungeonTrialFactory.create_batch_async(
            count,
            session_id=self.data['dungeon_session'].session_id,
            **kwargs
        )
        self.data['trials'] = trials
        return self
    
    def build(self) -> Dict[str, Any]:
        """Build and return the test data."""
        return self.data.copy()


class MockAPIClient:
    """Mock API client for testing external service interactions."""
    
    def __init__(self):
        self.responses = {}
        self.call_history = []
    
    def set_response(self, endpoint: str, response: Any):
        """Set a mock response for an endpoint."""
        self.responses[endpoint] = response
    
    async def get(self, endpoint: str, **kwargs) -> Any:
        """Mock GET request."""
        self.call_history.append(('GET', endpoint, kwargs))
        return self.responses.get(endpoint, {})
    
    async def post(self, endpoint: str, data: Any = None, **kwargs) -> Any:
        """Mock POST request."""
        self.call_history.append(('POST', endpoint, data, kwargs))
        return self.responses.get(endpoint, {})
    
    def get_call_history(self) -> List[tuple]:
        """Get history of API calls."""
        return self.call_history.copy()
    
    def reset(self):
        """Reset mock state."""
        self.responses.clear()
        self.call_history.clear()


class PerformanceTracker:
    """Track performance metrics during tests."""
    
    def __init__(self):
        self.metrics = {}
        self.start_times = {}
    
    def start_timer(self, name: str):
        """Start timing an operation."""
        self.start_times[name] = asyncio.get_event_loop().time()
    
    def end_timer(self, name: str) -> float:
        """End timing and record duration."""
        if name not in self.start_times:
            raise ValueError(f"Timer '{name}' not started")
        
        duration = asyncio.get_event_loop().time() - self.start_times[name]
        self.metrics[name] = duration
        del self.start_times[name]
        return duration
    
    def get_metrics(self) -> Dict[str, float]:
        """Get all recorded metrics."""
        return self.metrics.copy()
    
    def assert_performance(self, name: str, max_duration: float):
        """Assert that an operation completed within time limit."""
        if name not in self.metrics:
            raise ValueError(f"No metrics recorded for '{name}'")
        
        actual_duration = self.metrics[name]
        assert actual_duration <= max_duration, (
            f"Operation '{name}' took {actual_duration:.3f}s, "
            f"expected <= {max_duration:.3f}s"
        )


@pytest.fixture
async def test_data_builder():
    """Provide a test data builder."""
    return TestDataBuilder()


@pytest.fixture
def mock_api_client():
    """Provide a mock API client."""
    return MockAPIClient()


@pytest.fixture
def performance_tracker():
    """Provide a performance tracker."""
    return PerformanceTracker()


@pytest.fixture
async def mock_cache_service():
    """Provide a mock cache service."""
    cache = MagicMock()
    cache.get = AsyncMock(return_value=None)
    cache.set = AsyncMock(return_value=True)
    cache.delete = AsyncMock(return_value=True)
    cache.clear_pattern = AsyncMock(return_value=0)
    return cache


class DatabaseTestMixin:
    """Mixin for database testing utilities."""
    
    @staticmethod
    async def count_records(session: AsyncSession, model) -> int:
        """Count records in a table."""
        from sqlalchemy import select
        result = await session.execute(select(func.count(model.id)))
        return result.scalar()
    
    @staticmethod
    async def clear_table(session: AsyncSession, model):
        """Clear all records from a table."""
        from sqlalchemy import delete
        await session.execute(delete(model))
        await session.commit()
    
    @staticmethod
    async def assert_record_exists(
        session: AsyncSession,
        model,
        **filters
    ):
        """Assert that a record exists with given filters."""
        from sqlalchemy import select
        query = select(model)
        for key, value in filters.items():
            query = query.where(getattr(model, key) == value)
        
        result = await session.execute(query)
        record = result.scalar_one_or_none()
        assert record is not None, f"No {model.__name__} found with filters: {filters}"
        return record


def async_test(func):
    """Decorator to run async test functions."""
    def wrapper(*args, **kwargs):
        return asyncio.run(func(*args, **kwargs))
    return wrapper


def pytest_configure():
    """Configure pytest with custom markers."""
    pytest.mark.integration = pytest.mark.integration
    pytest.mark.performance = pytest.mark.performance
    pytest.mark.slow = pytest.mark.slow