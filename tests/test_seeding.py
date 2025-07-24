"""
Comprehensive test suite for seeding functionality.

This module tests all aspects of the seeding process including:
- Unit tests for individual seeding functions
- Integration tests for the complete seeding process
- Data validation and integrity tests
- Performance tests
- Error handling tests
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.infrastructure.database.models.v2 import MovementCategory, SkillTreeNode, Movement
from scripts.seed import (
    generate_movement_categories_from_unified_library,
    generate_skill_tree_from_unified_library,
    calculate_movement_xp,
    get_stat_reward_type,
    create_database_engine,
    seed_data
)


class TestMovementCategoryGeneration:
    """Test movement category generation from unified library."""
    
    def test_generate_movement_categories_basic(self):
        """Test basic movement category generation."""
        categories = generate_movement_categories_from_unified_library()
        
        assert isinstance(categories, list)
        assert len(categories) == 18
        
        # Check first category structure
        first_category = categories[0]
        assert 'id' in first_category
        assert 'name' in first_category
        assert 'primary_stat' in first_category
        
    def test_movement_categories_unique_names(self):
        """Test that all movement categories have unique names."""
        categories = generate_movement_categories_from_unified_library()
        names = [cat['name'] for cat in categories]
        
        assert len(names) == len(set(names)), "Category names should be unique"
        
    def test_movement_categories_valid_stat_types(self):
        """Test that all categories have valid stat types."""
        categories = generate_movement_categories_from_unified_library()
        valid_stat_types = {'STR', 'END', 'TECH'}
        
        for category in categories:
            assert category['primary_stat'] in valid_stat_types


class TestSkillTreeGeneration:
    """Test skill tree generation from unified library."""
    
    def test_generate_skill_tree_basic(self):
        """Test basic skill tree generation."""
        skill_tree = generate_skill_tree_from_unified_library()
        
        # Should have 18 categories
        assert len(skill_tree) == 18, "Should have 18 categories"
        
        # Each category should have 5 levels
        for category_id, nodes in skill_tree.items():
            assert len(nodes) == 5, f"Category {category_id} should have 5 levels"
            
    def test_skill_tree_node_structure(self):
        """Test that skill tree nodes have the correct structure."""
        skill_tree = generate_skill_tree_from_unified_library()
        
        for category_id, nodes in skill_tree.items():
            for node in nodes:
                assert 'level' in node, "Node should have level"
                assert 'name' in node, "Node should have name"
                assert 'movements' in node, "Node should have movements"
                assert isinstance(node['movements'], list), "Movements should be a list"
                
    def test_skill_tree_movements_per_node(self):
        """Test that each skill tree node has movements."""
        skill_tree = generate_skill_tree_from_unified_library()
        
        for category_id, nodes in skill_tree.items():
            for node in nodes:
                assert len(node['movements']) > 0, f"Node {node['name']} should have movements"


class TestXPCalculation:
    """Test XP calculation functionality."""
    
    def test_calculate_movement_xp_basic(self):
        """Test basic XP calculation."""
        xp = calculate_movement_xp("Push-up", 1, 1)
        
        assert isinstance(xp, (int, float))
        assert xp > 0
        
    def test_calculate_movement_xp_scaling(self):
        """Test XP scaling with level."""
        xp_level_1 = calculate_movement_xp("Push-up", 1, 1)
        xp_level_3 = calculate_movement_xp("Push-up", 3, 1)
        xp_level_5 = calculate_movement_xp("Push-up", 5, 1)
        
        assert xp_level_1 < xp_level_3 < xp_level_5
        
    def test_calculate_movement_xp_different_movements(self):
        """Test XP calculation for different movements."""
        movements = ["Push-up", "Squat", "Plank"]
        xp_values = []
        
        for movement in movements:
            xp = calculate_movement_xp(movement, 1, 1)
            xp_values.append(xp)
            assert xp > 0
            
        # All should be positive
        assert all(xp > 0 for xp in xp_values)


class TestStatRewardMapping:
    """Test stat reward type mapping."""
    
    def test_get_stat_reward_type_valid_ids(self):
        """Test stat reward mapping for valid category IDs."""
        # Test a few category IDs
        for category_id in range(1, 19):  # 18 categories
            stat_type = get_stat_reward_type(category_id)
            assert stat_type in {'STR', 'END', 'TECH'}
            
    def test_get_stat_reward_type_invalid_id(self):
        """Test stat reward mapping for invalid category ID."""
        # Should handle invalid IDs gracefully
        stat_type = get_stat_reward_type(999)
        assert stat_type in {'STR', 'END', 'TECH'}  # Should return a default


class TestDatabaseEngine:
    """Test database engine creation."""
    
    def test_create_database_engine_basic(self):
        """Test basic database engine creation."""
        with patch('scripts.seed.get_settings') as mock_settings:
            mock_settings.return_value.DATABASE_URL = "postgresql://user:pass@localhost/db"
            
            engine = create_database_engine()
            assert engine is not None
            assert str(engine.url).startswith("postgresql+asyncpg://")
            
    def test_create_database_engine_url_normalization(self):
        """Test that database URLs are properly normalized."""
        test_cases = [
            "postgresql://user:pass@localhost/db",
            "postgres://user:pass@localhost/db", 
            "postgresql+psycopg2://user:pass@localhost/db",
        ]
        
        for input_url in test_cases:
            with patch('scripts.seed.get_settings') as mock_settings:
                mock_settings.return_value.DATABASE_URL = input_url
                
                engine = create_database_engine()
                # Just verify it contains asyncpg driver
                assert "asyncpg" in str(engine.url)


class TestSeedDataIntegration:
    """Integration tests for the complete seeding process."""
    
    @pytest.mark.asyncio
    async def test_seed_data_with_mock_session(self):
        """Test seed_data function with mocked database session."""
        # Mock the database session and engine
        mock_session = AsyncMock(spec=AsyncSession)
        mock_engine = AsyncMock()
        
        # Mock query results to simulate empty database
        mock_result = Mock()
        mock_result.scalar_one_or_none = Mock(return_value=None)
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.commit = AsyncMock()
        mock_session.flush = AsyncMock()
        mock_session.add = Mock()  # add is synchronous
        
        with patch('scripts.seed.create_database_engine', return_value=mock_engine):
            with patch('scripts.seed.sessionmaker') as mock_sessionmaker:
                mock_sessionmaker.return_value.return_value.__aenter__.return_value = mock_session
                
                # Run the seeding function
                await seed_data()
                
                # Verify session operations were called
                assert mock_session.execute.called
                assert mock_session.commit.called
                
    @pytest.mark.asyncio
    async def test_seed_data_idempotency_simulation(self):
        """Test that seed_data is idempotent (simulated)."""
        mock_session = AsyncMock(spec=AsyncSession)
        mock_engine = AsyncMock()
        
        # Mock query results to simulate empty database
        mock_result = Mock()
        mock_result.scalar_one_or_none = Mock(return_value=None)
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.commit = AsyncMock()
        mock_session.flush = AsyncMock()
        mock_session.add = Mock()  # add is synchronous
        
        with patch('scripts.seed.create_database_engine', return_value=mock_engine):
            with patch('scripts.seed.sessionmaker') as mock_sessionmaker:
                mock_sessionmaker.return_value.return_value.__aenter__.return_value = mock_session
                
                await seed_data()
                
                # Verify add operations were called
                assert mock_session.add.called
                
    @pytest.mark.asyncio
    async def test_seed_data_error_handling(self):
        """Test error handling in seed_data function."""
        with patch('scripts.seed.create_database_engine') as mock_create_engine:
            # Simulate database connection error
            mock_create_engine.side_effect = Exception("Database connection failed")
            
            with pytest.raises(Exception):
                await seed_data()


class TestDataValidation:
    """Test data validation and integrity."""
    
    def test_movement_categories_data_volume(self):
        """Test that we generate the expected number of categories."""
        categories = generate_movement_categories_from_unified_library()
        assert len(categories) == 18, "Should generate exactly 18 V2 categories"
        
    def test_skill_tree_data_volume(self):
        """Test that we generate the expected number of skill tree nodes."""
        skill_tree = generate_skill_tree_from_unified_library()
        
        # 18 categories × 5 levels = 90 nodes total
        total_nodes = sum(len(nodes) for nodes in skill_tree.values())
        assert total_nodes == 90, "Should generate exactly 90 skill tree nodes"
        
    def test_movements_data_volume(self):
        """Test that we generate sufficient movements."""
        skill_tree = generate_skill_tree_from_unified_library()
        
        total_movements = 0
        for category_id, nodes in skill_tree.items():
            for node in nodes:
                total_movements += len(node['movements'])
        
        assert total_movements >= 90, "Should generate at least 90 movements"
        
    def test_data_consistency(self):
        """Test data consistency across generation functions."""
        categories = generate_movement_categories_from_unified_library()
        skill_tree = generate_skill_tree_from_unified_library()
        
        # Check that all skill tree categories have corresponding movement categories
        category_ids = {cat['id'] for cat in categories}
        skill_tree_category_ids = set(skill_tree.keys())
        
        assert skill_tree_category_ids.issubset(category_ids), "All skill tree categories should have corresponding movement categories"
            
        # Check that stat types are consistent
        for category in categories:
            stat_type = get_stat_reward_type(category['id'])
            assert stat_type == category['primary_stat']


class TestPerformance:
    """Performance tests for seeding operations."""
    
    def test_category_generation_performance(self):
        """Test that category generation completes in reasonable time."""
        import time
        
        start_time = time.time()
        categories = generate_movement_categories_from_unified_library()
        end_time = time.time()
        
        assert len(categories) > 0, "Should generate categories"
        assert end_time - start_time < 5.0, "Category generation should complete within 5 seconds"
        
    def test_skill_tree_generation_performance(self):
        """Test that skill tree generation completes in reasonable time."""
        import time
        
        start_time = time.time()
        skill_tree = generate_skill_tree_from_unified_library()
        end_time = time.time()
        
        assert len(skill_tree) > 0, "Should generate skill tree"
        assert end_time - start_time < 5.0, "Skill tree generation should complete within 5 seconds"
        
    def test_xp_calculation_performance(self):
        """Test XP calculation performance."""
        import time
        
        start_time = time.time()
        for i in range(1000):
            xp = calculate_movement_xp("Push-up", 1, 1)
            assert xp > 0
        end_time = time.time()
        
        assert (end_time - start_time) < 1.0, "1000 XP calculations should complete in under 1 second"


if __name__ == "__main__":
    pytest.main([__file__])