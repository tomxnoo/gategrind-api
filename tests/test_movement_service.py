"""
Comprehensive tests for the MovementService class.

This test suite covers unit and integration testing for the MovementService,
including database operations, error handling, and service lifecycle management.
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from app.application.services.movement_service import MovementService
from app.infrastructure.database.models.v2.movement_categories import MovementCategory
from app.infrastructure.database.models.v2.skill_tree_nodes import SkillTreeNode
from app.infrastructure.database.models.v2.movements import Movement


class TestMovementService:
    """Test suite for MovementService functionality."""
    
    @pytest.fixture
    def mock_session(self):
        """Create a mock async session."""
        session = AsyncMock(spec=AsyncSession)
        return session
    
    @pytest.fixture
    def movement_service(self, mock_session):
        """Create a MovementService instance with mocked session."""
        return MovementService(session=mock_session)
    
    @pytest.fixture
    def sample_category(self):
        """Create a sample MovementCategory for testing."""
        return MovementCategory(
            id="PULL_VERTICAL",
            name="Vertical Pulling",
            primary_stat="STR"
        )
    
    @pytest.fixture
    def sample_skill_tree_node(self):
        """Create a sample SkillTreeNode for testing."""
        return SkillTreeNode(
            id=1,
            category_id="PULL_VERTICAL",
            level=1,
            name="Foundation",
            description="Basic vertical pulling movements",
            required_ascendant_level=1,
            required_str_points=0,
            required_end_points=0,
            required_tech_points=0
        )
    
    @pytest.fixture
    def sample_movement(self):
        """Create a sample Movement for testing."""
        return Movement(
            id=1,
            node_id=1,
            name="Dead Hang",
            xp_per_rep=10.0,
            stat_reward_type="STR"
        )
    
    @pytest.mark.asyncio
    async def test_get_movement_categories_success(self, movement_service, mock_session, sample_category):
        """Test successful retrieval of movement categories."""
        # Mock the database query result
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_category]
        mock_session.execute.return_value = mock_result
        
        # Execute the method
        categories = await movement_service.get_movement_categories()
        
        # Verify results
        assert len(categories) == 1
        assert categories[0]["id"] == "PULL_VERTICAL"
        assert categories[0]["name"] == "Vertical Pulling"
        assert categories[0]["primary_stat"] == "STR"
    
    @pytest.mark.asyncio
    async def test_get_movement_category_success(self, movement_service, mock_session, sample_category, sample_skill_tree_node, sample_movement):
        """Test successful retrieval of a specific movement category."""
        # Set up relationships
        sample_skill_tree_node.movements = [sample_movement]
        sample_category.skill_tree_nodes = [sample_skill_tree_node]
        
        # Mock the database query result
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_category
        mock_session.execute.return_value = mock_result
        
        # Execute the method
        category = await movement_service.get_movement_category("PULL_VERTICAL")
        
        # Verify results
        assert category is not None
        assert category["id"] == "PULL_VERTICAL"
        assert category["name"] == "Vertical Pulling"
        assert len(category["skill_tree"]) == 1
        
        skill_node = category["skill_tree"][0]
        assert skill_node["level"] == 1
        assert skill_node["name"] == "Foundation"
        assert skill_node["requirements"]["ascendant_level"] == 1
        assert len(skill_node["movements"]) == 1
        
        movement = skill_node["movements"][0]
        assert movement["name"] == "Dead Hang"
        assert movement["xp_per_rep"] == 10.0
    
    @pytest.mark.asyncio
    async def test_get_movement_category_not_found(self, movement_service, mock_session):
        """Test retrieval of non-existent movement category."""
        # Mock the database query result for not found
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result
        
        # Execute the method
        category = await movement_service.get_movement_category("NON_EXISTENT")
        
        # Verify results
        assert category is None
    
    @pytest.mark.asyncio
    async def test_get_skill_tree_library_success(self, movement_service, mock_session, sample_category, sample_skill_tree_node, sample_movement):
        """Test successful retrieval of the complete skill tree library."""
        # Set up relationships
        sample_skill_tree_node.movements = [sample_movement]
        sample_category.skill_tree_nodes = [sample_skill_tree_node]
        
        # Mock the database query result
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_category]
        mock_session.execute.return_value = mock_result
        
        # Execute the method
        library = await movement_service.get_skill_tree_library()
        
        # Verify results
        assert "categories" in library
        assert len(library["categories"]) == 1
        
        category = library["categories"][0]
        assert category["id"] == "PULL_VERTICAL"
        assert len(category["skill_tree"]) == 1
        
        skill_node = category["skill_tree"][0]
        assert skill_node["level"] == 1
        assert len(skill_node["movements"]) == 1
    
    @pytest.mark.asyncio
    async def test_health_check_success(self, movement_service, mock_session, sample_category):
        """Test successful health check."""
        # Mock the database query result
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_category]
        mock_session.execute.return_value = mock_result
        
        # Execute the method
        health = await movement_service.health_check()
        
        # Verify results
        assert health["service"] == "MovementService"
        assert health["status"] == "healthy"
        assert health["database_connection"] == "ok"
        assert health["categories_count"] == 1
    
    @pytest.mark.asyncio
    async def test_health_check_failure(self, movement_service, mock_session):
        """Test health check when database is unavailable."""
        # Mock database error
        mock_session.execute.side_effect = SQLAlchemyError("Database connection failed")
        
        # Execute the method
        health = await movement_service.health_check()
        
        # Verify results
        assert health["service"] == "MovementService"
        assert health["status"] == "unhealthy"
        assert "error" in health
    
    @pytest.mark.asyncio
    async def test_database_error_handling(self, movement_service, mock_session):
        """Test proper error handling for database errors."""
        # Mock database error
        mock_session.execute.side_effect = SQLAlchemyError("Database error")
        
        # Test that errors are properly raised
        with pytest.raises(SQLAlchemyError):
            await movement_service.get_movement_categories()
    
    @pytest.mark.asyncio
    async def test_transaction_handling(self, movement_service):
        """Test transaction management."""
        # Mock operation
        async def mock_operation(session):
            return "success"
        
        # Test successful transaction
        result = await movement_service.execute_in_transaction(mock_operation)
        assert result == "success"
    
    def test_url_normalization(self, movement_service):
        """Test database URL normalization."""
        # Test postgresql:// to postgresql+asyncpg://
        url = "postgresql://user:pass@localhost/db"
        normalized = movement_service._normalize_db_url(url)
        assert normalized == "postgresql+asyncpg://user:pass@localhost/db"
        
        # Test postgres:// to postgresql+asyncpg://
        url = "postgres://user:pass@localhost/db"
        normalized = movement_service._normalize_db_url(url)
        assert normalized == "postgresql+asyncpg://user:pass@localhost/db"
        
        # Test already normalized URL
        url = "postgresql+asyncpg://user:pass@localhost/db"
        normalized = movement_service._normalize_db_url(url)
        assert normalized == "postgresql+asyncpg://user:pass@localhost/db"
    
    def test_url_normalization_other_drivers(self, movement_service):
        """Test URL normalization for non-postgres drivers."""
        url = "sqlite:///test.db"
        normalized = movement_service._normalize_db_url(url)
        assert normalized == "sqlite:///test.db"
    
    @pytest.mark.asyncio
    async def test_data_serialization(self, movement_service, mock_session):
        """Test proper data serialization in API responses."""
        # Create test data with complex relationships
        category = MovementCategory(
            id="TEST_CATEGORY",
            name="Test Category",
            primary_stat="STR"
        )
        
        node = SkillTreeNode(
            id=1,
            category_id="TEST_CATEGORY",
            level=2,
            name="Test Node",
            description="Test Description",
            required_ascendant_level=1,
            required_str_points=0,
            required_end_points=0,
            required_tech_points=0
        )
        
        movement = Movement(
            id=1,
            node_id=1,
            name="Test Movement",
            xp_per_rep=15.0,
            stat_reward_type="STR"
        )
        
        # Set up relationships
        node.movements = [movement]
        category.skill_tree_nodes = [node]
        
        # Mock the database query result
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = category
        mock_session.execute.return_value = mock_result
        
        # Execute the method
        result = await movement_service.get_movement_category("TEST_CATEGORY")
        
        # Verify proper serialization
        assert isinstance(result, dict)
        assert result["id"] == "TEST_CATEGORY"
        assert result["skill_tree"][0]["level"] == 2
        assert result["skill_tree"][0]["requirements"]["ascendant_level"] == 1
        assert result["skill_tree"][0]["movements"][0]["xp_per_rep"] == 15.0