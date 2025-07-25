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
            aura=525,  # Correct calculated aura for user with default stats: (5*100) + (1*10+1*10+1*5) + (0*25) = 500 + 25 + 0 = 525
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
        """Test aura calculation and update using Story 4.1 formula."""
        # Mock skill progress query
        mock_skill_result = MagicMock()
        mock_skill_result.scalars.return_value.all.return_value = [
            MagicMock(),  # 2 unlocked skills
            MagicMock()
        ]
        mock_session.execute.return_value = mock_skill_result
        
        # Calculate aura
        new_aura = await progression_service._calculate_and_update_aura(mock_session, user_with_stats)
        
        # Verify calculation using Story 4.1 formula:
        # (Level * 100) + (STR*10 + END*10 + TECH*5) + (Nodes Unlocked * 25)
        # Base: level 5 * 100 = 500
        # Stats: (3*10 + 2*10 + 4*5) = 30 + 20 + 20 = 70
        # Skills: 2 * 25 = 50
        # Total: 500 + 70 + 50 = 620
        expected_aura = 620
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


class TestMilestoneProgression:
    """Test suite for milestone progression functionality."""
    
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
            aura=525,  # Correct calculated aura: (5*100) + (1*10+1*10+1*5) + (0*25) = 500 + 25 + 0 = 525
            strength_points=10,
            endurance_points=10,
            technique_points=10,
            rested_xp_pool=0
        )
        return user
    
    @pytest.fixture
    def sample_user_with_stats(self):
        """Create a sample user with stats for milestone testing."""
        user = Ascendant(
            id=1,
            discord_id="123456789",
            username="testuser",
            level=5,
            global_xp=1000,
            aura=65,  # Correct calculated aura: (5*10) + (1+1+1)*5 = 50 + 15 = 65
            strength_points=10,
            endurance_points=10,
            technique_points=10,
            rested_xp_pool=0
        )
        
        stats = AscendantStats(
            ascendant_id=1,
            str_level=1,
            str_xp=0,
            end_level=1,
            end_xp=0,
            tech_level=1,
            tech_xp=0,
            str_value=10,  # Default stat values
            end_value=10,
            tech_value=10
        )
        
        user.stats = stats
        return user
    
    def test_check_stat_milestones_no_milestones(self, progression_service):
        """Test milestone detection when no milestones are crossed."""
        milestones = progression_service._check_stat_milestones(50, 100)
        assert milestones == []
    
    def test_check_stat_milestones_single_milestone(self, progression_service):
        """Test milestone detection for a single milestone."""
        # From 100 to 200 should cross the 150 milestone
        milestones = progression_service._check_stat_milestones(100, 200)
        assert milestones == [150]
    
    def test_check_stat_milestones_multiple_milestones(self, progression_service):
        """Test milestone detection for multiple milestones."""
        # From 50 to 500 should cross 150, 300, and 450 milestones
        milestones = progression_service._check_stat_milestones(50, 500)
        assert milestones == [150, 300, 450]
    
    def test_check_stat_milestones_exact_milestone_start(self, progression_service):
        """Test milestone detection when starting exactly at a milestone."""
        # From 150 to 350 should cross 300 milestone only
        milestones = progression_service._check_stat_milestones(150, 350)
        assert milestones == [300]
    
    def test_check_stat_milestones_exact_milestone_end(self, progression_service):
        """Test milestone detection when ending exactly at a milestone."""
        # From 50 to 150 should cross the 150 milestone
        milestones = progression_service._check_stat_milestones(50, 150)
        assert milestones == [150]
    
    def test_check_stat_milestones_large_gap(self, progression_service):
        """Test milestone detection with a large XP gap."""
        # From 0 to 1000 should cross 150, 300, 450, 600, 750, 900 milestones
        milestones = progression_service._check_stat_milestones(0, 1000)
        expected = [150, 300, 450, 600, 750, 900]
        assert milestones == expected
    
    def test_check_stat_milestones_zero_start(self, progression_service):
        """Test milestone detection starting from zero XP."""
        # From 0 to 200 should cross the 150 milestone
        milestones = progression_service._check_stat_milestones(0, 200)
        assert milestones == [150]
    
    @pytest.mark.asyncio
    async def test_add_stat_xp_with_single_milestone(self, progression_service, mock_session, sample_user_with_stats):
        """Test adding stat XP that triggers a single milestone."""
        # Set initial XP to 100, add 100 to reach 200 (crosses 150 milestone)
        sample_user_with_stats.stats.str_xp = 100
        
        # Mock database query
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_user_with_stats
        mock_session.execute.return_value = mock_result
        
        # Add XP that will trigger milestone
        result = await progression_service.add_xp(1, 100, 'strength')
        
        # Verify milestone achievement
        assert result.user_id == 1
        assert result.xp_added == 100
        assert result.category == 'strength'
        assert 'strength' in result.milestone_rewards
        assert result.milestone_rewards['strength'] == [150]
        
        # Verify stat points awarded for milestone
        assert result.stat_points_awarded['strength_points'] == 1  # 1 milestone = 1 stat point
        assert sample_user_with_stats.strength_points == 11  # 10 + 1
    
    @pytest.mark.asyncio
    async def test_add_stat_xp_with_multiple_milestones(self, progression_service, mock_session, sample_user_with_stats):
        """Test adding stat XP that triggers multiple milestones."""
        # Set initial XP to 50, add 400 to reach 450 (crosses 150, 300, 450 milestones)
        sample_user_with_stats.stats.end_xp = 50
        
        # Mock database query
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_user_with_stats
        mock_session.execute.return_value = mock_result
        
        # Add XP that will trigger multiple milestones
        result = await progression_service.add_xp(1, 400, 'endurance')
        
        # Verify milestone achievements
        assert result.user_id == 1
        assert result.xp_added == 400
        assert result.category == 'endurance'
        assert 'endurance' in result.milestone_rewards
        assert result.milestone_rewards['endurance'] == [150, 300, 450]
        
        # Verify stat points awarded for milestones + level-ups
        # 450 XP = level 2 (1 level gained) + 3 milestones = 4 total points
        assert result.stat_points_awarded['endurance_points'] == 4  # 3 milestones + 1 level-up = 4 stat points
        assert sample_user_with_stats.endurance_points == 14  # 10 + 4
    
    @pytest.mark.asyncio
    async def test_add_stat_xp_no_milestones(self, progression_service, mock_session, sample_user_with_stats):
        """Test adding stat XP that doesn't trigger any milestones."""
        # Set initial XP to 100, add 30 to reach 130 (no milestones crossed)
        sample_user_with_stats.stats.tech_xp = 100
        
        # Mock database query
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_user_with_stats
        mock_session.execute.return_value = mock_result
        
        # Add XP that won't trigger milestones
        result = await progression_service.add_xp(1, 30, 'technique')
        
        # Verify no milestone achievements
        assert result.user_id == 1
        assert result.xp_added == 30
        assert result.category == 'technique'
        assert result.milestone_rewards == {}  # No milestones achieved
        
        # Verify no stat points awarded for milestones
        assert 'technique_points' not in result.stat_points_awarded or result.stat_points_awarded['technique_points'] == 0
        assert sample_user_with_stats.technique_points == 10  # No change
    
    @pytest.mark.asyncio
    async def test_milestone_rewards_in_result_to_dict(self, progression_service):
        """Test that milestone rewards are included in ProgressionResult.to_dict()."""
        result = ProgressionResult()
        result.user_id = 1
        result.xp_added = 200
        result.category = 'strength'
        result.milestone_rewards = {'strength': [150, 300]}
        result.stat_points_awarded = {'strength_points': 2}
        result.level_changes = {}
        result.new_aura = 100
        result.previous_aura = 100
        
        result_dict = result.to_dict()
        
        # Verify milestone rewards are included
        assert 'milestone_rewards' in result_dict
        assert result_dict['milestone_rewards'] == {'strength': [150, 300]}
    
    @pytest.mark.asyncio
    async def test_milestone_with_level_up_combination(self, progression_service, mock_session, sample_user_with_stats):
        """Test milestone achievement combined with level-up."""
        # Set stats to trigger both milestone and level-up
        sample_user_with_stats.stats.str_xp = 100  # Will cross 150 milestone
        sample_user_with_stats.stats.str_level = 1  # Low level for easy level-up
        
        # Mock database query
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_user_with_stats
        mock_session.execute.return_value = mock_result
        
        # Add XP that will trigger both milestone and level-up
        result = await progression_service.add_xp(1, 300, 'strength')
        
        # Verify both milestone and level-up occurred
        assert result.user_id == 1
        assert result.category == 'strength'
        assert 'strength' in result.milestone_rewards
        assert len(result.milestone_rewards['strength']) > 0  # At least one milestone
        assert 'strength' in result.level_changes  # Level-up occurred
        
        # Verify stat points from both sources
        milestone_points = len(result.milestone_rewards['strength'])
        level_points = result.level_changes['strength']['gained'] if 'strength' in result.level_changes else 0
        total_expected = milestone_points + level_points
        assert result.stat_points_awarded['strength_points'] == total_expected
    
    @pytest.mark.asyncio
    async def test_milestone_configuration_custom_interval(self, mock_session):
        """Test milestone detection with custom interval configuration."""
        # Create service with custom milestone interval
        service = ProgressionService(session=mock_session)
        service.milestone_interval = 100  # Custom interval of 100 instead of default 150
        
        # Test milestone detection with custom interval
        milestones = service._check_stat_milestones(50, 350)
        expected = [100, 200, 300]  # Should use 100 interval
        assert milestones == expected
    
    @pytest.mark.asyncio
    async def test_milestone_edge_case_exact_boundaries(self, progression_service):
        """Test milestone detection at exact boundary conditions."""
        # Test various boundary conditions
        assert progression_service._check_stat_milestones(149, 150) == [150]
        assert progression_service._check_stat_milestones(150, 151) == []
        assert progression_service._check_stat_milestones(149, 151) == [150]
        assert progression_service._check_stat_milestones(299, 301) == [300]
    
    @pytest.mark.asyncio
    async def test_milestone_performance_large_numbers(self, progression_service):
        """Test milestone detection performance with large XP values."""
        # Test with very large XP values to ensure no performance issues
        start_time = asyncio.get_event_loop().time()
        milestones = progression_service._check_stat_milestones(0, 100000)
        end_time = asyncio.get_event_loop().time()
        
        # Should complete quickly (less than 1 second)
        assert (end_time - start_time) < 1.0
        
        # Should find correct number of milestones
        expected_count = 100000 // 150  # 666 milestones
        assert len(milestones) == expected_count

    # Tests for add_stat_rewards method (Approach A)
    @pytest.mark.asyncio
    async def test_add_stat_rewards_success(self, progression_service, mock_session, sample_user_with_stats):
        """Test successful stat rewards addition."""
        # Mock database query
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_user_with_stats
        mock_session.execute.return_value = mock_result
        
        # Add stat rewards
        result = await progression_service.add_stat_rewards(1, str_reward=5, end_reward=3, tech_reward=2)
        
        # Verify results
        assert result.user_id == 1
        assert result.category == ''  # category is not set for stat rewards
        assert result.stat_rewards_awarded['str_reward'] == 5
        assert result.stat_rewards_awarded['end_reward'] == 3
        assert result.stat_rewards_awarded['tech_reward'] == 2
        
        # Verify stats were updated
        assert sample_user_with_stats.stats.str_value == 15  # 10 + 5
        assert sample_user_with_stats.stats.end_value == 13  # 10 + 3
        assert sample_user_with_stats.stats.tech_value == 12  # 10 + 2
    
    @pytest.mark.asyncio
    async def test_add_stat_rewards_partial(self, progression_service, mock_session, sample_user_with_stats):
        """Test adding only some stat rewards."""
        # Mock database query
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_user_with_stats
        mock_session.execute.return_value = mock_result
        
        # Add only strength and technique rewards
        result = await progression_service.add_stat_rewards(1, str_reward=3, tech_reward=4)
        
        # Verify results
        assert result.user_id == 1
        assert result.category == ''  # category is not set for stat rewards
        assert result.stat_rewards_awarded['str_reward'] == 3
        assert result.stat_rewards_awarded['end_reward'] == 0
        assert result.stat_rewards_awarded['tech_reward'] == 4
        
        # Verify stats were updated correctly
        assert sample_user_with_stats.stats.str_value == 13  # 10 + 3
        assert sample_user_with_stats.stats.end_value == 10  # No change
        assert sample_user_with_stats.stats.tech_value == 14  # 10 + 4
    
    @pytest.mark.asyncio
    async def test_add_stat_rewards_zero_values(self, progression_service):
        """Test adding stat rewards with all zero values raises error."""
        # Test that error is raised for all zero values
        with pytest.raises(ValueError, match="At least one stat reward must be greater than 0"):
            await progression_service.add_stat_rewards(1, str_reward=0, end_reward=0, tech_reward=0)
    
    @pytest.mark.asyncio
    async def test_add_stat_rewards_creates_stats_if_missing(self, progression_service, mock_session, sample_user):
        """Test that stats are created if they don't exist when adding stat rewards."""
        # User without stats
        sample_user.stats = None
        
        # Mock database query
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_user
        mock_session.execute.return_value = mock_result
        
        # Add stat rewards
        result = await progression_service.add_stat_rewards(1, str_reward=2, end_reward=1, tech_reward=3)
        
        # Verify stats were created
        assert sample_user.stats is not None
        assert sample_user.stats.ascendant_id == 1
        
        # Verify stat rewards were applied
        assert result.stat_rewards_awarded['str_reward'] == 2
        assert result.stat_rewards_awarded['end_reward'] == 1
        assert result.stat_rewards_awarded['tech_reward'] == 3
        assert sample_user.stats.str_value == 12  # 10 (default) + 2
        assert sample_user.stats.end_value == 11  # 10 (default) + 1
        assert sample_user.stats.tech_value == 13  # 10 (default) + 3
    
    @pytest.mark.asyncio
    async def test_add_stat_rewards_negative_values_error(self, progression_service):
        """Test error handling for negative stat reward values."""
        with pytest.raises(ValueError, match="Stat rewards must be non-negative"):
            await progression_service.add_stat_rewards(1, str_reward=-1, end_reward=2, tech_reward=1)
        
        with pytest.raises(ValueError, match="Stat rewards must be non-negative"):
            await progression_service.add_stat_rewards(1, str_reward=1, end_reward=-2, tech_reward=1)
        
        with pytest.raises(ValueError, match="Stat rewards must be non-negative"):
            await progression_service.add_stat_rewards(1, str_reward=1, end_reward=2, tech_reward=-1)
    
    @pytest.mark.asyncio
    async def test_add_stat_rewards_user_not_found_error(self, progression_service, mock_session):
        """Test error handling when user is not found for stat rewards."""
        # Mock database query returning None
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result
        
        # Test that error is raised
        with pytest.raises(Exception, match="User with ID 999 not found"):
            await progression_service.add_stat_rewards(999, str_reward=1, end_reward=1, tech_reward=1)
    
    @pytest.mark.asyncio
    async def test_add_stat_rewards_aura_update(self, progression_service, mock_session, sample_user_with_stats):
        """Test that aura is updated when adding stat rewards."""
        # Mock database query
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_user_with_stats
        mock_session.execute.return_value = mock_result
        
        # Store initial aura
        initial_aura = sample_user_with_stats.aura
        
        # Add stat rewards
        result = await progression_service.add_stat_rewards(1, str_reward=2, end_reward=2, tech_reward=2)
        
        # Verify aura was updated
        assert result.new_aura >= initial_aura  # Aura should increase or stay same
        assert result.previous_aura == initial_aura
        assert sample_user_with_stats.aura == result.new_aura
    
    @pytest.mark.asyncio
    async def test_stat_rewards_result_to_dict(self):
        """Test ProgressionResult to_dict conversion for stat rewards."""
        result = ProgressionResult()
        result.user_id = 1
        result.category = ''  # category is not set for stat rewards
        result.stat_rewards_awarded = {'str_reward': 3, 'end_reward': 2, 'tech_reward': 1}
        result.level_changes = {}
        result.milestone_rewards = {}
        result.stat_points_awarded = {}
        result.new_aura = 150
        result.previous_aura = 140
        
        result_dict = result.to_dict()
        
        # Verify stat rewards are included
        assert 'stat_rewards_awarded' in result_dict
        assert result_dict['stat_rewards_awarded'] == {'str_reward': 3, 'end_reward': 2, 'tech_reward': 1}
        assert result_dict['category'] == ''
        assert result_dict['aura_change']['new'] == 150
        assert result_dict['aura_change']['previous'] == 140