"""
Comprehensive tests for the ProgressionService class.

This test suite covers unit and integration testing for the ProgressionService,
including XP addition, level calculations, aura updates, and error handling.
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from app.application.services.progression_service import ProgressionService, ProgressionResult
from app.infrastructure.database.models.v2.ascendants import Ascendant
from app.infrastructure.database.models.v2.stats import AscendantStats
from app.infrastructure.database.models.v2.user_skill_progress import UserSkillProgress


class TestProgressionService:
    """Test suite for ProgressionService functionality."""
    
    @pytest.fixture
    def mock_session(self):
        """Create a mock async session."""
        session = AsyncMock(spec=AsyncSession)
        return session
    
    @pytest.fixture
    def progression_service(self, mock_session):
        """Create a ProgressionService instance with mocked session."""
        service = ProgressionService(session=mock_session)
        # Mock the execute_in_transaction method to directly call the function
        async def mock_execute_in_transaction(func):
            return await func(mock_session)
        service.execute_in_transaction = mock_execute_in_transaction
        return service
    
    @pytest.fixture
    def sample_user(self):
        """Create a sample Ascendant user for testing."""
        user = Ascendant(
            id=1,
            discord_id="123456789",
            username="testuser",
            level=5,
            global_xp=1000,
            aura=100,
            strength_points=10,
            endurance_points=10,
            technique_points=10,
            rested_xp_pool=0
        )
        return user
    
    @pytest.fixture
    def sample_stats(self):
        """Create sample AscendantStats for testing."""
        stats = AscendantStats(
            ascendant_id=1,
            str_level=3,
            str_xp=300,
            end_level=2,
            end_xp=200,
            tech_level=4,
            tech_xp=500
        )
        return stats
    
    @pytest.fixture
    def user_with_stats(self, sample_user, sample_stats):
        """Create a user with stats relationship."""
        sample_user.stats = sample_stats
        return sample_user
    
    @pytest.mark.asyncio
    async def test_add_global_xp_no_level_up(self, progression_service, mock_session, sample_user):
        """Test adding global XP without triggering a level-up."""
        # Mock database query
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_user
        mock_session.execute.return_value = mock_result
        
        # Add XP that won't cause level-up
        result = await progression_service.add_xp(1, 50, 'global')
        
        # Verify results
        assert result.user_id == 1
        assert result.xp_added == 50
        assert result.category == 'global'
        assert len(result.level_changes) == 0  # No level-up
        assert len(result.stat_points_awarded) == 0
        assert sample_user.global_xp == 1050
        assert sample_user.level == 5  # No change
    
    @pytest.mark.asyncio
    async def test_add_global_xp_with_level_up(self, progression_service, mock_session, sample_user):
        """Test adding global XP that triggers a level-up."""
        # Set user to be close to level-up (level 4 requires 1602 XP, level 5 requires 2720 XP)
        sample_user.global_xp = 2000  # Level 4 with some extra XP
        sample_user.level = 4
        
        # Mock database query
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_user
        mock_session.execute.return_value = mock_result
        
        # Add XP that will cause level-up (2000 + 1000 = 3000, which is level 5)
        result = await progression_service.add_xp(1, 1000, 'global')
        
        # Verify results
        assert result.user_id == 1
        assert result.xp_added == 1000
        assert result.category == 'global'
        assert 'global' in result.level_changes
        assert result.level_changes['global']['previous'] == 4
        assert result.level_changes['global']['new'] == 5
        assert result.stat_points_awarded['strength_points'] > 0
        assert result.stat_points_awarded['endurance_points'] > 0
        assert result.stat_points_awarded['technique_points'] > 0
    
    @pytest.mark.asyncio
    async def test_add_stat_xp_strength(self, progression_service, mock_session, user_with_stats):
        """Test adding XP to strength stat."""
        # Mock database query
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = user_with_stats
        mock_session.execute.return_value = mock_result
        
        # Add strength XP
        result = await progression_service.add_xp(1, 100, 'strength')
        
        # Verify results
        assert result.user_id == 1
        assert result.xp_added == 100
        assert result.category == 'strength'
        assert user_with_stats.stats.str_xp == 400  # 300 + 100
    
    @pytest.mark.asyncio
    async def test_add_stat_xp_with_level_up(self, progression_service, mock_session, user_with_stats):
        """Test adding stat XP that triggers a stat level-up."""
        # Set strength to be close to level-up (level 3 requires 802 XP, level 4 requires 1602 XP)
        user_with_stats.stats.str_xp = 1000  # Level 3 with some extra XP
        user_with_stats.stats.str_level = 3
        
        # Mock database query
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = user_with_stats
        mock_session.execute.return_value = mock_result
        
        # Add XP that will cause level-up (1000 + 800 = 1800, which is level 4)
        result = await progression_service.add_xp(1, 800, 'strength')
        
        # Verify results
        assert result.user_id == 1
        assert result.category == 'strength'
        assert 'strength' in result.level_changes
        assert result.level_changes['strength']['previous'] == 3
        assert result.level_changes['strength']['new'] == 4
    
    @pytest.mark.asyncio
    async def test_add_xp_creates_stats_if_missing(self, progression_service, mock_session, sample_user):
        """Test that stats are created if they don't exist when adding stat XP."""
        # User without stats
        sample_user.stats = None
        
        # Mock database query
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_user
        mock_session.execute.return_value = mock_result
        
        # Add stat XP
        result = await progression_service.add_xp(1, 100, 'endurance')
        
        # Verify stats were created
        assert sample_user.stats is not None
        assert sample_user.stats.ascendant_id == 1
        assert sample_user.stats.end_xp == 100
    
    @pytest.mark.asyncio
    async def test_calculate_level_from_xp(self, progression_service):
        """Test level calculation from XP."""
        # Test various XP amounts
        assert progression_service._calculate_level_from_xp(0) == 1
        assert progression_service._calculate_level_from_xp(100) == 1  # Not enough for level 2
        assert progression_service._calculate_level_from_xp(300) == 2  # Level 2 requires ~282 XP
        assert progression_service._calculate_level_from_xp(1000) == 3  # Should be level 3
    
    @pytest.mark.asyncio
    async def test_calculate_xp_for_level(self, progression_service):
        """Test XP requirement calculation for specific levels."""
        # Level 1 requires 0 XP
        assert progression_service._calculate_xp_for_level(1) == 0
        
        # Level 2 requires 100 * (2^1.5) ≈ 282.84 XP
        level_2_xp = progression_service._calculate_xp_for_level(2)
        assert abs(level_2_xp - 282.84) < 1
        
        # Level 3 requires additional 100 * (3^1.5) ≈ 519.61 XP
        level_3_xp = progression_service._calculate_xp_for_level(3)
        assert level_3_xp > level_2_xp
    
    @pytest.mark.asyncio
    async def test_aura_calculation(self, progression_service, mock_session, user_with_stats):
        """Test aura calculation and update."""
        # Mock skill progress query
        mock_skill_result = MagicMock()
        mock_skill_result.scalars.return_value.all.return_value = [
            MagicMock(),  # 2 unlocked skills
            MagicMock()
        ]
        mock_session.execute.return_value = mock_skill_result
        
        # Calculate aura
        new_aura = await progression_service._calculate_and_update_aura(mock_session, user_with_stats)
        
        # Verify calculation
        # Base: level 5 * 10 = 50
        # Stats: (3 + 2 + 4) * 5 = 45
        # Skills: 2 * 15 = 30
        # Total: 50 + 45 + 30 = 125
        expected_aura = 125
        assert new_aura == expected_aura
        assert user_with_stats.aura == expected_aura
    
    @pytest.mark.asyncio
    async def test_calculate_level_progress_global(self, progression_service, mock_session, sample_user):
        """Test level progress calculation for global category."""
        # Mock database query
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_user
        mock_session.execute.return_value = mock_result
        
        # Mock get_session
        progression_service.get_session = AsyncMock(return_value=mock_session)
        
        # Calculate progress
        progress = await progression_service.calculate_level_progress(1, 'global')
        
        # Verify results
        assert progress['current_level'] == 5
        assert progress['current_xp'] == 1000
        assert 'next_level_xp_required' in progress
        assert 'progress_percentage' in progress
        assert 'xp_to_next_level' in progress
    
    @pytest.mark.asyncio
    async def test_calculate_level_progress_stat(self, progression_service, mock_session, user_with_stats):
        """Test level progress calculation for stat category."""
        # Mock database query
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = user_with_stats
        mock_session.execute.return_value = mock_result
        
        # Mock get_session
        progression_service.get_session = AsyncMock(return_value=mock_session)
        
        # Calculate progress for strength
        progress = await progression_service.calculate_level_progress(1, 'strength')
        
        # Verify results
        assert progress['current_level'] == 3
        assert progress['current_xp'] == 300
        assert 'next_level_xp_required' in progress
        assert 'progress_percentage' in progress
    
    @pytest.mark.asyncio
    async def test_invalid_category_error(self, progression_service):
        """Test error handling for invalid XP category."""
        with pytest.raises(ValueError, match="Invalid category"):
            await progression_service.add_xp(1, 100, 'invalid_category')
    
    @pytest.mark.asyncio
    async def test_negative_xp_error(self, progression_service):
        """Test error handling for negative XP amount."""
        with pytest.raises(ValueError, match="XP amount must be positive"):
            await progression_service.add_xp(1, -50, 'global')
    
    @pytest.mark.asyncio
    async def test_zero_xp_error(self, progression_service):
        """Test error handling for zero XP amount."""
        with pytest.raises(ValueError, match="XP amount must be positive"):
            await progression_service.add_xp(1, 0, 'global')
    
    @pytest.mark.asyncio
    async def test_user_not_found_error(self, progression_service, mock_session):
        """Test error handling when user is not found."""
        # Mock database query returning None
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result
        
        # Test that error is raised
        with pytest.raises(Exception, match="User with ID 999 not found"):
            await progression_service.add_xp(999, 100, 'global')
    
    @pytest.mark.asyncio
    async def test_database_error_handling(self, progression_service, mock_session):
        """Test proper error handling for database errors."""
        # Mock database error
        mock_session.execute.side_effect = SQLAlchemyError("Database error")
        
        # Test that errors are properly raised
        with pytest.raises(SQLAlchemyError):
            await progression_service.add_xp(1, 100, 'global')
    
    @pytest.mark.asyncio
    async def test_health_check_success(self, progression_service, mock_session, sample_user):
        """Test successful health check."""
        # Mock database query
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_user]
        mock_session.execute.return_value = mock_result
        
        # Mock get_session
        progression_service.get_session = AsyncMock(return_value=mock_session)
        
        # Execute health check
        health = await progression_service.health_check()
        
        # Verify results
        assert health["service"] == "ProgressionService"
        assert health["status"] == "healthy"
        assert health["database_connection"] == "ok"
        assert health["users_count"] == 1
    
    @pytest.mark.asyncio
    async def test_health_check_failure(self, progression_service, mock_session):
        """Test health check when database is unavailable."""
        # Mock database error
        mock_session.execute.side_effect = SQLAlchemyError("Database connection failed")
        
        # Mock get_session
        progression_service.get_session = AsyncMock(return_value=mock_session)
        
        # Execute health check
        health = await progression_service.health_check()
        
        # Verify results
        assert health["service"] == "ProgressionService"
        assert health["status"] == "unhealthy"
        assert "error" in health
    
    @pytest.mark.asyncio
    async def test_progression_result_to_dict(self):
        """Test ProgressionResult to_dict conversion."""
        result = ProgressionResult()
        result.user_id = 1
        result.xp_added = 100
        result.category = 'global'
        result.level_changes = {'global': {'previous': 5, 'new': 6, 'gained': 1}}
        result.stat_points_awarded = {'strength_points': 1, 'endurance_points': 1, 'technique_points': 1}
        result.new_aura = 150
        result.previous_aura = 100
        
        result_dict = result.to_dict()
        
        # Verify conversion
        assert result_dict['user_id'] == 1
        assert result_dict['xp_added'] == 100
        assert result_dict['category'] == 'global'
        assert result_dict['level_changes'] == {'global': {'previous': 5, 'new': 6, 'gained': 1}}
        assert result_dict['stat_points_awarded'] == {'strength_points': 1, 'endurance_points': 1, 'technique_points': 1}
        assert result_dict['aura_change']['previous'] == 100
        assert result_dict['aura_change']['new'] == 150
        assert result_dict['aura_change']['difference'] == 50
    
    @pytest.mark.asyncio
    async def test_multiple_level_ups(self, progression_service, mock_session, sample_user):
        """Test handling multiple level-ups from a single XP addition."""
        # Set user to low level with minimal XP
        sample_user.level = 1
        sample_user.global_xp = 0
        
        # Mock database query
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_user
        mock_session.execute.return_value = mock_result
        
        # Add large amount of XP to trigger multiple level-ups
        result = await progression_service.add_xp(1, 2000, 'global')
        
        # Verify multiple levels gained
        assert 'global' in result.level_changes
        assert result.level_changes['global']['gained'] > 1
        assert result.stat_points_awarded['strength_points'] > 1
    
    @pytest.mark.asyncio
    async def test_skill_bonus_calculation_error_handling(self, progression_service, mock_session, sample_user):
        """Test skill bonus calculation with database error."""
        # Mock skill progress query to raise error
        mock_session.execute.side_effect = [
            # First call for user query succeeds
            MagicMock(scalar_one_or_none=MagicMock(return_value=sample_user)),
            # Second call for skill progress fails
            SQLAlchemyError("Skill query failed")
        ]
        
        # Calculate skill bonus (should handle error gracefully)
        skill_bonus = await progression_service._calculate_skill_bonus(mock_session, 1)
        
        # Should return 0 on error
        assert skill_bonus == 0
    
    @pytest.mark.asyncio
    async def test_edge_case_max_level_safety(self, progression_service):
        """Test safety check for extremely high levels."""
        # Test with very high XP that could cause infinite loop
        very_high_xp = 10000000  # 10 million XP
        level = progression_service._calculate_level_from_xp(very_high_xp)
        
        # Should not exceed reasonable max level (1000)
        assert level <= 1000
    
    @pytest.mark.asyncio
    async def test_calculate_level_progress_no_stats(self, progression_service, mock_session, sample_user):
        """Test level progress calculation when user has no stats."""
        # User without stats
        sample_user.stats = None
        
        # Mock database query
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_user
        mock_session.execute.return_value = mock_result
        
        # Mock get_session
        progression_service.get_session = AsyncMock(return_value=mock_session)
        
        # Calculate progress for strength (should return defaults)
        progress = await progression_service.calculate_level_progress(1, 'strength')
        
        # Verify default values
        assert progress['current_level'] == 1
        assert progress['current_xp'] == 0
        assert progress['progress_percentage'] == 0.0