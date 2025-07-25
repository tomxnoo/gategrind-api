"""
Pytest configuration and fixtures for GateGrind V2 tests.
"""
import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.infrastructure.database.models.v2 import Base





@pytest.fixture(scope="function")
async def db_engine():
    """Create an in-memory SQLite database engine for testing."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    await engine.dispose()


@pytest.fixture(scope="function")
async def db_session(db_engine):
    """Create a database session for testing."""
    async_session = sessionmaker(
        db_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        yield session


@pytest.fixture
def sample_ascendant_data():
    """Sample data for creating Ascendant instances."""
    return {
        "discord_id": "123456789012345678",
        "username": "test_user",
        "level": 5,
        "global_xp": 1000,
        "aura": 525,  # Correct calculated aura: (5*100) + (1*10+1*10+1*5) + (0*25) = 500 + 25 + 0 = 525
        "strength_points": 3,
        "endurance_points": 2,
        "technique_points": 1,
        "rested_xp_pool": 100
    }


@pytest.fixture
def sample_movement_category_data():
    """Sample data for creating a MovementCategory."""
    return {
        "id": "PULL_VERTICAL",
        "name": "Vertical Pulling",
        "primary_stat": "STR"
    }


@pytest.fixture
def sample_skill_tree_node_data(sample_movement_category_data):
    """Sample data for creating a SkillTreeNode."""
    return {
        "node_id": "PULL_VERTICAL_1",
        "category_id": sample_movement_category_data["id"],
        "level": 1,
        "name": "Foundation",
        "description": "Basic vertical pulling movements",
        "required_ascendant_level": 1,
        "required_str_points": 0,
        "required_end_points": 0,
        "required_tech_points": 0
    }


@pytest.fixture
def sample_movement_data():
    """Sample data for creating Movement instances."""
    return {
        "name": "Negative Pull-ups",
        "xp_per_rep": 1.5,
        "stat_reward_type": "STR"
    }