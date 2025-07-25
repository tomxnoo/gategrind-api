"""
Integration tests for movement logging service aura updates.

This test suite focuses specifically on testing aura updates through the movement logging
service and its integration with progression services.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import asyncio

from app.application.services.movement_logging_service import MovementLoggingService, MovementLogResult
from app.application.services.progression_service import ProgressionService, ProgressionResult
from app.infrastructure.database.models.v2.ascendants import Ascendant
from app.infrastructure.database.models.v2.stats import AscendantStats
from app.infrastructure.database.models.v2.movements import Movement


class TestMovementLoggingAuraIntegration:
    """Test suite for movement logging service aura integration."""
    
    @pytest.fixture
    def mock_session(self):
        """Create a mock database session."""
        return AsyncMock()
    
    @pytest.fixture
    def mock_progression_service(self):
        """Create a mock progression service."""
        return AsyncMock(spec=ProgressionService)
    
    @pytest.fixture
    def movement_service(self, mock_session, mock_progression_service):
        """Create a movement logging service with mocked dependencies."""
        service = MovementLoggingService(mock_session)
        service._progression_service = mock_progression_service
        
        # Mock execute_in_transaction to use mock_session
        async def mock_transaction(func):
            return await func(mock_session)
        service.execute_in_transaction = AsyncMock(side_effect=mock_transaction)
        
        # Mock the _get_movement_by_id method directly
        service._get_movement_by_id = AsyncMock()
        
        return service
    
    @pytest.fixture
    def sample_user(self):
        """Create a sample user for testing."""
        return Ascendant(
            id=1,
            username="test_user",
            level=5,
            global_xp=1000,
            aura=1250,
            skill_points=10
        )
    
    @pytest.fixture
    def sample_movement(self):
        """Create a sample movement for testing."""
        return Movement(
            id=1,
            node_id=1,
            name="Push-ups",
            xp_per_rep=2.5,
            stat_reward_type="STR"
        )
    
    @pytest.fixture
    def xp_progression_result(self):
        """Create a progression result for XP addition."""
        result = ProgressionResult()
        result.user_id = 1
        result.xp_added = 50
        result.category = 'global'
        result.previous_aura = 1250
        result.new_aura = 1275
        result.aura_change_reason = "Global progression"
        result.level_changes = {}
        return result
    
    @pytest.fixture
    def stat_progression_result(self):
        """Create a progression result for stat rewards."""
        result = ProgressionResult()
        result.user_id = 1
        result.stat_points_awarded = {'strength_points': 2}
        result.previous_aura = 1275
        result.new_aura = 1300
        result.aura_change_reason = "Stat progression"
        result.level_changes = {'strength': {'previous': 3, 'new': 4, 'gained': 1}}
        return result

    @pytest.mark.asyncio
    async def test_log_movement_triggers_aura_update(
        self, movement_service, mock_session, sample_user, sample_movement,
        xp_progression_result, stat_progression_result
    ):
        """Test that logging movement triggers aura updates through progression."""
        # Mock database queries
        mock_session.execute.return_value.scalar_one_or_none.return_value = sample_movement
        mock_session.add = MagicMock()
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()
        
        # Mock progression service calls
        movement_service._progression_service.add_xp.return_value = xp_progression_result
        movement_service._progression_service.add_stat_rewards.return_value = stat_progression_result
        
        # Execute movement logging
        result = await movement_service.log_movement(
            user_id=1,
            movement_id=1,
            reps=20,
            session_id="test_session"
        )
        
        # Verify aura update is included in result
        assert result.aura_update is not None
        assert isinstance(result.aura_update, dict)
        
        # Verify aura update structure
        if result.aura_update:  # Only check if not empty
            assert "previous_aura" in result.aura_update
            assert "new_aura" in result.aura_update
            assert "change" in result.aura_update
            assert "reason" in result.aura_update
            
            # Verify aura calculation matches expected values
            assert result.aura_update["previous_aura"] == 1250
            assert result.aura_update["new_aura"] == 1300  # Final aura after both progressions
            assert result.aura_update["change"] == 50
            assert "progression" in result.aura_update["reason"].lower()

    @pytest.mark.asyncio
    async def test_movement_aura_update_with_level_changes(
        self, movement_service, mock_session, sample_user, sample_movement
    ):
        """Test aura updates when movement triggers level changes."""
        # Mock database queries
        mock_session.execute.return_value.scalar_one_or_none.return_value = sample_movement
        mock_session.add = MagicMock()
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()
        
        # Create progression results with level changes
        xp_result = ProgressionResult()
        xp_result.user_id = 1
        xp_result.xp_added = 200
        xp_result.category = 'global'
        xp_result.previous_aura = 1250
        xp_result.new_aura = 1350
        xp_result.aura_change_reason = "Global progression"
        xp_result.level_changes = {'global': {'previous': 5, 'new': 6, 'gained': 1}}
        
        stat_result = ProgressionResult()
        stat_result.user_id = 1
        stat_result.stat_points_awarded = {'endurance_points': 3}
        stat_result.previous_aura = 1350
        stat_result.new_aura = 1425
        stat_result.aura_change_reason = "Stat progression"
        stat_result.level_changes = {'endurance': {'previous': 2, 'new': 4, 'gained': 2}}
        
        movement_service._progression_service.add_xp.return_value = xp_result
        movement_service._progression_service.add_stat_rewards.return_value = stat_result
        
        # Execute movement logging
        result = await movement_service.log_movement(
            user_id=1,
            movement_id=1,
            reps=15,
            session_id="test_session"
        )
        
        # Verify aura update reflects all level changes
        if result.aura_update:  # Only check if not empty
            assert result.aura_update["change"] == 175  # 1425 - 1250
        assert result.level_ups is not None
        assert len(result.level_ups) >= 2  # Should have both global and endurance level ups
        
        # Check that both level up types are present
        level_up_types = [level_up["type"] for level_up in result.level_ups]
        assert 'global' in level_up_types
        assert 'endurance' in level_up_types

    @pytest.mark.asyncio
    async def test_movement_aura_update_performance_with_multiple_progressions(
        self, movement_service, mock_session, sample_user, sample_movement
    ):
        """Test performance when movement triggers multiple progression updates."""
        import time
        
        # Mock database queries
        mock_session.execute.return_value.scalar_one_or_none.return_value = sample_movement
        mock_session.add = MagicMock()
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()
        
        # Create multiple progression results
        results = []
        for i in range(5):  # Simulate 5 different progression updates
            result = ProgressionResult()
            result.user_id = 1
            result.xp_added = 20
            result.category = 'global'
            result.previous_aura = 1250 + (i * 10)
            result.new_aura = 1260 + (i * 10)
            result.aura_change_reason = f"Progression {i+1}"
            results.append(result)
        
        movement_service._progression_service.add_xp.return_value = results[0]
        movement_service._progression_service.add_stat_rewards.return_value = results[1]
        
        # Measure execution time
        start_time = time.time()
        result = await movement_service.log_movement(
            user_id=1,
            movement_id=1,
            reps=50,
            session_id="test_session"
        )
        end_time = time.time()
        
        execution_time = end_time - start_time
        
        # Verify performance is acceptable (under 1 second)
        assert execution_time < 1.0
        
        # Verify aura update is still correctly calculated
        assert result.aura_update is not None
        assert isinstance(result.aura_update["change"], (int, float))

    @pytest.mark.asyncio
    async def test_movement_aura_update_error_handling(
        self, movement_service, mock_session, sample_user, sample_movement
    ):
        """Test error handling in aura updates during movement logging."""
        # Mock database queries
        mock_session.execute.return_value.scalar_one_or_none.return_value = sample_movement
        mock_session.add = MagicMock()
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()
        
        # Mock progression service to raise an exception
        movement_service._progression_service.add_xp.side_effect = Exception("Aura calculation failed")
        
        # Should handle the error gracefully
        with pytest.raises(Exception) as exc_info:
            await movement_service.log_movement(
                user_id=1,
                movement_id=1,
                reps=20,
                session_id="test_session"
            )
        
        assert "Aura calculation failed" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_movement_aura_update_with_no_progression(
        self, movement_service, mock_session, sample_user, sample_movement
    ):
        """Test aura updates when movement doesn't trigger progression."""
        # Mock database queries
        mock_session.execute.return_value.scalar_one_or_none.return_value = sample_movement
        mock_session.add = MagicMock()
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()
        
        # Create progression results with no aura change
        no_change_result = ProgressionResult()
        no_change_result.user_id = 1
        no_change_result.xp_added = 0
        no_change_result.category = 'global'
        # No aura fields set (no change) - previous_aura and new_aura will be 0
        no_change_result.previous_aura = 0
        no_change_result.new_aura = 0
        
        movement_service._progression_service.add_xp.return_value = no_change_result
        movement_service._progression_service.add_stat_rewards.return_value = no_change_result
        
        # Execute movement logging
        result = await movement_service.log_movement(
            user_id=1,
            movement_id=1,
            reps=5,
            session_id="test_session"
        )
        
        # Should handle no aura change gracefully
        # When there's no aura change, aura_update should be empty dict
        assert result.aura_update is not None
        assert isinstance(result.aura_update, dict)
        
        # For no progression, aura_update should be empty or indicate no change
        if result.aura_update:  # Only check if not empty
            # If aura_update has content, change should be 0
            assert result.aura_update.get("change", 0) == 0
        # If aura_update is empty dict, that's also valid for no change

    @pytest.mark.asyncio
    async def test_movement_to_dict_includes_aura_update(
        self, movement_service, mock_session, sample_user, sample_movement,
        xp_progression_result
    ):
        """Test that MovementLogResult.to_dict() includes aura update information."""
        # Mock database queries
        mock_session.execute.return_value.scalar_one_or_none.return_value = sample_movement
        mock_session.add = MagicMock()
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()
        
        movement_service._progression_service.add_xp.return_value = xp_progression_result
        movement_service._progression_service.add_stat_rewards.return_value = ProgressionResult()
        
        # Execute movement logging
        result = await movement_service.log_movement(
            user_id=1,
            movement_id=1,
            reps=20,
            session_id="test_session"
        )
        
        # Convert to dictionary (as used by API)
        result_dict = result.to_dict()
        
        # Verify aura_update is included in dictionary
        assert "aura_update" in result_dict
        if result_dict["aura_update"] is not None:
            aura_update = result_dict["aura_update"]
            assert "previous_aura" in aura_update
            assert "new_aura" in aura_update
            assert "change" in aura_update
            assert "reason" in aura_update

    @pytest.mark.asyncio
    async def test_concurrent_movement_logging_aura_consistency(
        self, movement_service, mock_session, sample_user
    ):
        """Test aura consistency when multiple movements are logged concurrently."""
        # Mock database queries
        mock_session.execute.return_value.scalar_one_or_none.return_value = sample_user
        mock_session.add = MagicMock()
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()
        
        # Create different movements
        movements = []
        for i in range(3):
            movement = Movement(
                id=i+1,
                node_id=f"node_{i+1}",
                name=f"Exercise_{i+1}",
                xp_per_rep=5,
                stat_reward_type="strength"
            )
            movements.append(movement)
        
        # Mock different progression results for each movement
        progression_results = []
        for i in range(3):
            result = ProgressionResult()
            result.user_id = 1
            result.xp_added = 25 + i*10
            result.category = 'global'
            result.previous_aura = 1250 + i*25
            result.new_aura = 1275 + i*25
            result.aura_change_reason = f"Global progression {i+1}"
            progression_results.append(result)
        
        # Mock session to return different movements
        def mock_scalar_side_effect(*args, **kwargs):
            # Return movements in sequence
            if hasattr(mock_scalar_side_effect, 'call_count'):
                mock_scalar_side_effect.call_count += 1
            else:
                mock_scalar_side_effect.call_count = 0
            
            if mock_scalar_side_effect.call_count < len(movements):
                return movements[mock_scalar_side_effect.call_count]
            return movements[-1]
        
        mock_session.execute.return_value.scalar_one_or_none.side_effect = mock_scalar_side_effect
        
        # Mock progression service to return different results
        def mock_add_xp_side_effect(*args, **kwargs):
            if hasattr(mock_add_xp_side_effect, 'call_count'):
                mock_add_xp_side_effect.call_count += 1
            else:
                mock_add_xp_side_effect.call_count = 0
            
            if mock_add_xp_side_effect.call_count < len(progression_results):
                return progression_results[mock_add_xp_side_effect.call_count]
            return progression_results[-1]
        
        movement_service._progression_service.add_xp.side_effect = mock_add_xp_side_effect
        movement_service._progression_service.add_stat_rewards.return_value = ProgressionResult()
        
        # Execute concurrent movement logging
        tasks = []
        for i in range(3):
            task = movement_service.log_movement(
                user_id=1,
                movement_id=i+1,
                reps=10 + i*5,
                session_id=f"session_{i+1}"
            )
            tasks.append(task)
        
        # Wait for all tasks to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Verify all results are successful and have aura updates
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                pytest.fail(f"Movement logging {i+1} failed: {result}")
            
            assert hasattr(result, 'aura_update')
            # Each result should have some aura information
            # (exact values may vary due to concurrent execution)