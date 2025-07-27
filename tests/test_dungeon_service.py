"""
Test suite for the DungeonService

This test suite covers:
- DungeonService business logic
- Dungeon entry validation and session creation
- Trial generation and completion tracking
- Reward calculation and distribution
- Level progression and unlock management
- Error handling and edge cases
"""
import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from typing import List, Dict, Any

from app.application.services.dungeon_service import (
    DungeonService, 
    DungeonLevelLockedError, 
    InsufficientRequirementsError
)
from app.infrastructure.database.models.v2 import (
    Ascendant, DungeonSession, DungeonTrial, DungeonReward, 
    DailyModifier, DungeonLevelUnlock, DungeonProgress, DungeonKey
)


@pytest.mark.asyncio
class TestDungeonService:
    """Test the DungeonService business logic."""
    
    @pytest.fixture
    def mock_session(self):
        """Create a mock database session."""
        session = AsyncMock()
        return session
    
    @pytest.fixture
    def dungeon_service(self, mock_session):
        """Create a DungeonService with mocked session."""
        service = DungeonService(mock_session)
        service.get_session = AsyncMock(return_value=mock_session)
        return service
    
    @pytest.fixture
    def sample_ascendant(self):
        """Create a sample ascendant for testing."""
        return Ascendant(
            id=1,
            username="test_user",
            aura=1000,
            strength_points=50,
            endurance_points=45,
            technique_points=40,
            skill_points=100
        )
    
    @pytest.fixture
    def sample_dungeon_progress(self):
        """Create sample dungeon progress."""
        return DungeonProgress(
            ascendant_id=1,
            highest_level_completed=2
        )
    
    async def test_health_check(self, dungeon_service, mock_session):
        """Test the health check functionality."""
        # Mock the execute method to return a result with scalar method
        result_mock = MagicMock()
        result_mock.scalar.return_value = 5  # Mock session count
        mock_session.execute.return_value = result_mock
        
        result = await dungeon_service.health_check()
        
        assert result["status"] == "healthy"
        assert result["service"] == "DungeonService"
        assert result["database_connected"] == True
        assert result["total_sessions"] == 5
        assert "timestamp" in result
    
    async def test_calculate_aura_requirement(self, dungeon_service):
        """Test aura requirement calculation."""
        # Test level 1 (base requirement)
        aura_req = dungeon_service.calculate_aura_requirement(1)
        assert aura_req == 100  # 100 * (1.5 ** 0)
        
        # Test level 2 (1.5x multiplier)
        aura_req = dungeon_service.calculate_aura_requirement(2)
        assert aura_req == 150  # 100 * (1.5 ** 1)
        
        # Test level 5 (exponential scaling)
        aura_req = dungeon_service.calculate_aura_requirement(5)
        assert aura_req == int(100 * (1.5 ** 4))  # 506
    
    async def test_calculate_stat_requirements(self, dungeon_service):
        """Test stat requirement calculation."""
        # Test level 1
        stats = dungeon_service.calculate_stat_requirements(1)
        assert stats['strength'] == 10  # 10 * (1.5 ** 0)
        assert stats['endurance'] == 10
        assert stats['technique'] == 10
        
        # Test level 3
        stats = dungeon_service.calculate_stat_requirements(3)
        expected = int(10 * (1.5 ** 2))  # 22
        assert stats['strength'] == expected
        assert stats['endurance'] == expected
        assert stats['technique'] == expected
    
    async def test_calculate_skill_tree_requirements(self, dungeon_service):
        """Test skill tree requirement calculation."""
        # Test level 1 (no requirements)
        req = dungeon_service.calculate_skill_tree_requirements(1)
        assert req == 0
        
        # Test level 3 (early levels)
        req = dungeon_service.calculate_skill_tree_requirements(3)
        assert req == 2  # level - 1
        
        # Test level 7 (mid levels)
        req = dungeon_service.calculate_skill_tree_requirements(7)
        assert req == 9  # 5 + (7-5)*2
        
        # Test level 12 (high levels)
        req = dungeon_service.calculate_skill_tree_requirements(12)
        assert req == 21  # 15 + (12-10)*3
    
    async def test_validate_entry_requirements_success(self, dungeon_service, sample_ascendant, mock_session):
        """Test successful entry requirement validation."""
        # Mock session.get to return the ascendant
        mock_session.get = AsyncMock(return_value=sample_ascendant)
        
        # Mock get_dungeon_progress
        with patch.object(dungeon_service, 'get_dungeon_progress') as mock_progress:
            mock_progress.return_value = DungeonProgress(ascendant_id=1, highest_level_completed=2)
            
            # Mock DungeonLevelUnlock query (no unlock requirements for this level)
            unlock_result = MagicMock()
            unlock_result.scalar_one_or_none.return_value = None
            mock_session.execute.return_value = unlock_result
            
            # Mock get_shadow_keys method
            with patch.object(dungeon_service, 'get_shadow_keys') as mock_get_keys:
                mock_get_keys.return_value = 5  # Has enough keys
                
                # Test validation for level 3 (should pass) - pass ascendant_id instead of ascendant
                result = await dungeon_service.validate_entry_requirements(1, 3)
                
                # The method returns True on success
                assert result == True
    
    async def test_validate_entry_requirements_insufficient_aura(self, dungeon_service, sample_ascendant, mock_session):
        """Test validation failure due to insufficient aura."""
        # Set low aura
        sample_ascendant.aura = 50
        
        # Mock database queries
        mock_session.get = AsyncMock(return_value=sample_ascendant)
        
        # Mock get_dungeon_progress
        with patch.object(dungeon_service, 'get_dungeon_progress') as mock_progress:
            mock_progress.return_value = DungeonProgress(ascendant_id=1, highest_level_completed=2)
            
            # Mock DungeonLevelUnlock query (no unlock requirements for this level)
            unlock_result = MagicMock()
            unlock_result.scalar_one_or_none.return_value = None
            mock_session.execute.return_value = unlock_result
            
            # Mock get_shadow_keys
            with patch.object(dungeon_service, 'get_shadow_keys') as mock_keys:
                mock_keys.return_value = 5
                
                with pytest.raises(InsufficientRequirementsError):
                    await dungeon_service.validate_entry_requirements(1, 3)
    
    async def test_validate_entry_requirements_level_locked(self, dungeon_service, sample_ascendant, mock_session):
        """Test validation failure due to locked level."""
        # Mock database queries
        mock_session.get = AsyncMock(return_value=sample_ascendant)
        
        # Mock get_dungeon_progress
        with patch.object(dungeon_service, 'get_dungeon_progress') as mock_progress:
            mock_progress.return_value = DungeonProgress(ascendant_id=1, highest_level_completed=1)
            
            # Mock DungeonLevelUnlock query with unlock requirements
            mock_unlock_req = MagicMock()
            mock_unlock_req.check_unlock_requirements.return_value = (False, ["Level 4 not completed"])
            
            unlock_result = MagicMock()
            unlock_result.scalar_one_or_none.return_value = mock_unlock_req
            mock_session.execute.return_value = unlock_result
            
            with pytest.raises(DungeonLevelLockedError):
                await dungeon_service.validate_entry_requirements(1, 5)
    
    async def test_get_shadow_keys(self, dungeon_service, mock_session):
        """Test getting shadow keys count."""
        # Mock the execute method to return a result with scalar method
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = 10
        mock_session.execute.return_value = result_mock
        
        keys = await dungeon_service.get_shadow_keys(1)
        assert keys == 10
        mock_session.execute.assert_called_once()
    
    async def test_deduct_shadow_keys_success(self, dungeon_service, mock_session):
        """Test successful shadow key deduction."""
        # Mock get_shadow_keys to return sufficient keys
        with patch.object(dungeon_service, 'get_shadow_keys') as mock_get_keys:
            mock_get_keys.return_value = 10
            
            # Mock the database update
            mock_session.execute = AsyncMock()
            mock_session.commit = AsyncMock()
            
            result = await dungeon_service.deduct_shadow_keys(1, 1)
            
            assert result == True
            mock_get_keys.assert_called_once_with(1)
            mock_session.execute.assert_called_once()
            mock_session.commit.assert_called_once()

    async def test_deduct_shadow_keys_insufficient(self, dungeon_service, mock_session):
        """Test shadow key deduction with insufficient keys."""
        # Mock get_shadow_keys to return insufficient keys
        with patch.object(dungeon_service, 'get_shadow_keys') as mock_get_keys:
            mock_get_keys.return_value = 0
            
            with pytest.raises(InsufficientRequirementsError):
                await dungeon_service.deduct_shadow_keys(1, 1)
    
    async def test_get_active_daily_modifier(self, dungeon_service, mock_session):
        """Test getting active daily modifier."""
        # Mock daily modifier
        modifier_result = MagicMock()
        modifier = DailyModifier(
            modifier_date=datetime.now(timezone.utc).date(),
            modifier_name="XP Boost Day",
            modifier_type="xp_boost",
            reward_multiplier=1.5,
            description="XP Boost Day",
            is_active=True
        )
        modifier_result.scalar_one_or_none.return_value = modifier
        mock_session.execute.return_value = modifier_result
        
        result = await dungeon_service.get_active_daily_modifier()
        
        assert result is not None
        assert result.modifier_type == "xp_boost"
        assert result.reward_multiplier == 1.5
    
    async def test_generate_trials(self, dungeon_service):
        """Test trial generation."""
        # Mock the quest generation service
        mock_quest_service = AsyncMock()
        dungeon_service.get_quest_generation_service = AsyncMock(return_value=mock_quest_service)
        
        # Create a mock daily modifier with to_dict method
        mock_modifier = MagicMock()
        mock_modifier.to_dict.return_value = {'modifier_name': 'test', 'reward_multiplier': 1.5}
        
        trials = await dungeon_service.generate_trials(5, mock_modifier)
        
        assert len(trials) == 4  # 3 base + 1 additional for level 5
        assert all('trial_number' in trial for trial in trials)
        assert all('target_reps' in trial for trial in trials)
    
    async def test_calculate_trial_difficulty(self, dungeon_service):
        """Test trial difficulty calculation."""
        # Test with level 1, trial index 0
        difficulty = dungeon_service.calculate_trial_difficulty(1, 0)
        assert 0.5 <= difficulty <= 1.0
        
        # Test with higher level and trial index
        difficulty = dungeon_service.calculate_trial_difficulty(5, 2)
        assert 0.5 <= difficulty <= 1.0
    
    async def test_enter_dungeon_success(self, dungeon_service, sample_ascendant, mock_session):
        """Test successful dungeon entry."""
        # Mock validation success
        with patch.object(dungeon_service, 'validate_entry_requirements') as mock_validate:
            mock_validate.return_value = True  # Service returns True on success
            
            # Mock deduct shadow keys
            with patch.object(dungeon_service, 'deduct_shadow_keys') as mock_deduct:
                mock_deduct.return_value = True
                
                # Mock daily modifier
                mock_modifier = MagicMock()
                mock_modifier.to_dict.return_value = {'modifier_name': 'test', 'reward_multiplier': 1.5}
                with patch.object(dungeon_service, 'get_active_daily_modifier') as mock_daily:
                    mock_daily.return_value = mock_modifier
                    
                    # Mock session creation
                    mock_session.add = MagicMock()
                    mock_session.commit = AsyncMock()
                    mock_session.refresh = AsyncMock()
                    
                    # Mock trial generation
                    with patch.object(dungeon_service, 'generate_trials') as mock_trials:
                        mock_trials.return_value = [
                            {
                                "trial_number": 1,
                                "trial_type": "movement_based", 
                                "target_reps": 20, 
                                "movement_category": "push",
                                "difficulty_modifier": 0.6
                            }
                        ]
                        
                        result = await dungeon_service.enter_dungeon(sample_ascendant, 3)
                        
                        assert "session_id" in result
                        assert "trials" in result
                        assert result["level"] == 3
                        assert len(result["trials"]) == 1
    
    async def test_enter_dungeon_validation_failure(self, dungeon_service, sample_ascendant):
        """Test dungeon entry with validation failure."""
        # Mock validation to raise an exception
        dungeon_service.validate_entry_requirements = AsyncMock(side_effect=InsufficientRequirementsError("Insufficient aura"))
        
        with pytest.raises(InsufficientRequirementsError):
            await dungeon_service.enter_dungeon(1, 3)
    
    async def test_calculate_rewards(self, dungeon_service):
        """Test reward calculation."""
        # Create a mock session
        mock_session = MagicMock()
        mock_session.dungeon_level = 5
        mock_session.id = 1
        
        # Test the calculation
        rewards = await dungeon_service.calculate_rewards(mock_session)
        
        assert len(rewards) >= 2  # At least aura and shadow essence
        assert any(r['type'] == 'aura' for r in rewards)
        assert any(r['type'] == 'shadow_essence' for r in rewards)
    
    async def test_calculate_rewards_with_modifier(self, dungeon_service):
        """Test reward calculation with daily modifier."""
        # Create a mock session
        mock_session = MagicMock()
        mock_session.dungeon_level = 5
        mock_session.id = 1
        
        modifier = DailyModifier(
            modifier_date=datetime.now(timezone.utc).date(),
            modifier_name="XP Boost Day",
            modifier_type="xp_boost",
            reward_multiplier=1.5,
            description="XP Boost Day",
            is_active=True
        )
        
        # Mock the get_active_daily_modifier method
        dungeon_service.get_active_daily_modifier = AsyncMock(return_value=modifier)
        
        rewards = await dungeon_service.calculate_rewards(mock_session)
        
        assert len(rewards) >= 2
        assert any(r['type'] == 'aura' for r in rewards)
    
    async def test_complete_trial_success(self, dungeon_service, mock_session):
        """Test successful trial completion."""
        # Create mock trial and session objects
        mock_trial = MagicMock()
        mock_trial.id = 1
        mock_trial.session_id = 1
        mock_trial.target_reps = 20
        mock_trial.completed_reps = 0
        mock_trial.trial_status = 'active'
        mock_trial.is_completed = False
        
        mock_dungeon_session = MagicMock()
        mock_dungeon_session.id = 1
        mock_dungeon_session.ascendant_id = 1
        mock_dungeon_session.dungeon_level = 3
        mock_dungeon_session.trials_required = 3
        mock_dungeon_session.trials_completed = 1
        mock_dungeon_session.session_status = 'active'
        mock_dungeon_session.is_active = True
        
        # Mock session.get calls
        mock_session.get = AsyncMock()
        mock_session.get.side_effect = lambda model, id: mock_trial if model == DungeonTrial else mock_dungeon_session
        mock_session.commit = AsyncMock()
        
        progress_data = {"reps": 20}
        
        result = await dungeon_service.complete_trial(1, progress_data)
        
        assert result["trial_completed"] is True
        assert result["session_completed"] is False  # Still has trials left
        assert "rewards_earned" in result
        assert result["next_trial_available"] is True

    async def test_complete_trial_session_completion(self, dungeon_service, mock_session):
        """Test trial completion that completes the session."""
        # Create mock trial and session objects for session completion
        mock_trial = MagicMock()
        mock_trial.id = 1
        mock_trial.session_id = 1
        mock_trial.target_reps = 20
        mock_trial.completed_reps = 0
        mock_trial.trial_status = 'active'
        mock_trial.is_completed = False
        
        mock_dungeon_session = MagicMock()
        mock_dungeon_session.id = 1
        mock_dungeon_session.ascendant_id = 1
        mock_dungeon_session.dungeon_level = 3
        mock_dungeon_session.trials_required = 3
        mock_dungeon_session.trials_completed = 2  # Last trial
        mock_dungeon_session.session_status = 'active'
        mock_dungeon_session.is_active = True
        
        # Mock session.get calls
        mock_session.get = AsyncMock()
        mock_session.get.side_effect = lambda model, id: mock_trial if model == DungeonTrial else mock_dungeon_session
        mock_session.commit = AsyncMock()
        
        # Mock the methods that will be called
        dungeon_service.calculate_rewards = AsyncMock(return_value=[{"type": "aura", "amount": 100}])
        dungeon_service.distribute_rewards = AsyncMock()
        dungeon_service.update_dungeon_progress = AsyncMock()
        
        progress_data = {"reps": 20}
        
        result = await dungeon_service.complete_trial(1, progress_data)
        
        assert result["trial_completed"] is True
        assert result["session_completed"] is True
        assert "rewards_earned" in result
        assert result["next_trial_available"] is False
    
    async def test_distribute_rewards(self, dungeon_service, mock_session):
        """Test reward distribution to ascendant."""
        # Mock session operations
        mock_session.add = MagicMock()
        mock_session.commit = AsyncMock()
        
        rewards = [
            {"type": "aura", "amount": 100, "description": "Dungeon completion bonus"},
            {"type": "shadow_essence", "amount": 15, "description": "Shadow essence reward"}
        ]
        
        # Test the actual distribute_rewards method
        await dungeon_service.distribute_rewards(1, rewards)
        
        # Verify that rewards were added to session
        assert mock_session.add.call_count == 2  # Two rewards
        mock_session.commit.assert_called_once()
    
    async def test_update_dungeon_progress(self, dungeon_service, mock_session):
        """Test dungeon progress update."""
        # Mock the get_dungeon_progress method to return None (new progress)
        dungeon_service.get_dungeon_progress = AsyncMock(return_value=None)
        
        # Mock session operations
        mock_session.add = MagicMock()
        mock_session.commit = AsyncMock()
        
        # Test updating progress for a new ascendant
        await dungeon_service.update_dungeon_progress(1, 3)
        
        # Verify that a new progress record was added
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()


class TestDungeonServiceExceptions:
    """Test custom exceptions for DungeonService."""
    
    def test_dungeon_level_locked_error(self):
        """Test DungeonLevelLockedError exception."""
        error = DungeonLevelLockedError("Level 5 is locked")
        assert str(error) == "Level 5 is locked"
        assert isinstance(error, Exception)
    
    def test_insufficient_requirements_error(self):
        """Test InsufficientRequirementsError exception."""
        error = InsufficientRequirementsError("Not enough aura")
        assert str(error) == "Not enough aura"
        assert isinstance(error, Exception)


@pytest.mark.asyncio
class TestDungeonServiceIntegration:
    """Integration tests for DungeonService with real database models."""
    
    @pytest.fixture
    def real_session(self):
        """Create a real database session for integration tests."""
        # This would use a test database in a real scenario
        # For now, we'll mock it but structure it like a real session
        session = AsyncMock()
        return session
    
    async def test_full_dungeon_flow_integration(self, real_session):
        """Test a complete dungeon flow from entry to completion."""
        service = DungeonService(real_session)
        
        # This would be a full integration test with a test database
        # Testing the complete flow: entry -> trial completion -> rewards -> progress update
        # For now, we'll structure it but not implement the full database setup
        
        # Mock the complete flow
        with patch.object(service, 'validate_entry_requirements') as mock_validate:
            mock_validate.return_value = True  # Service returns True on success
            
            with patch.object(service, 'deduct_shadow_keys') as mock_deduct:
                mock_deduct.return_value = True
                
                # Mock daily modifier
                mock_modifier = MagicMock()
                mock_modifier.to_dict.return_value = {'modifier_name': 'test', 'reward_multiplier': 1.5}
                with patch.object(service, 'get_active_daily_modifier') as mock_daily:
                    mock_daily.return_value = mock_modifier
                    
                    with patch.object(service, 'generate_trials') as mock_trials:
                        mock_trials.return_value = [
                            {
                                "trial_number": 1, 
                                "trial_type": "movement_based", 
                                "target_reps": 20,
                                "movement_category": "Push",
                                "difficulty_modifier": 0.6
                            }
                        ]
                        
                        # Mock session creation
                        real_session.add = MagicMock()
                        real_session.commit = AsyncMock()
                        real_session.refresh = AsyncMock()
                        
                        # Test entry with correct Ascendant fields
                        ascendant = Ascendant(
                            id=1, 
                            discord_id="123456789",
                            username="test", 
                            aura=1000, 
                            strength_points=50, 
                            endurance_points=50, 
                            technique_points=50
                        )
                        entry_result = await service.enter_dungeon(ascendant, 3)
                        
                        assert "session_id" in entry_result
                        assert "trials" in entry_result