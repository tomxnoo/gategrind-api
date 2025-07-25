"""
Pytest configuration and fixtures for GateGrind V2 tests.
"""
import pytest
import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.infrastructure.database.models.v2 import Base


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
def db_engine():
    """Create an in-memory SQLite database engine for testing."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False
    )
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    yield engine
    
    # Clean up
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(db_engine):
    """Create a database session for testing."""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    session = SessionLocal()
    
    yield session
    
    session.close()


@pytest.fixture
def sample_ascendant_data():
    """Sample data for creating Ascendant instances."""
    return {
        "discord_id": "123456789012345678",
        "username": "test_user",
        "level": 5,
        "global_xp": 1000,
        "aura": 50,
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