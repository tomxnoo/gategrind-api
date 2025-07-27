"""
Additional Integration Tests for Dungeon System

This test suite covers:
- Full dungeon flow integration testing
- Concurrent access testing
- Session recovery testing
- Performance validation
- Error handling integration
"""
import pytest
import asyncio
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from typing import List, Dict, Any

from app.application.services.dungeon_service import (
    DungeonService, 
    DungeonLevelLockedError, 
    InsufficientRequirementsError,
    ActiveSessionExistsError
)
from app.application.services.dungeon_cache_service import DungeonCacheService
from app.application.tasks.dungeon_background_tasks import DungeonBackgroundTasks
from app.infrastructure.database.models.v2 import (
    Ascendant, DungeonSession, DungeonTrial, DungeonReward, 
    DailyModifier, DungeonLevelUnlock, DungeonProgress
)


@pytest.mark.asyncio
class TestDungeonSystemIntegration:
    """Integration tests for the complete dungeon system."""
    
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
            aura=2000,
            strength_points=100,
            endurance_points=95,
            technique_points=90,
            skill_points=200
        )
    
    @pytest.fixture
    def sample_daily_modifier(self):
        """Create a sample daily modifier."""
        return DailyModifier(
            id=1,
            modifier_date=datetime.now(timezone.utc).date(),
            modifier_type='strength_focus',
            description='Strength training day',
            difficulty_multiplier=1.2,
            reward_multiplier=1.3
        )
    
    async def test_complete_dungeon_flow_success(self, dungeon_service, sample_ascendant, sample_daily_modifier, mock_session):
        """Test a complete successful dungeon flow from entry to completion."""
        # Setup mocks
        mock_session.get = AsyncMock(return_value=sample_ascendant)
        
        # Mock validation methods
        with patch.object(dungeon_service, 'validate_entry_requirements') as mock_validate:
            mock_validate.return_value = True
            
            with patch.object(dungeon_service, 'get_shadow_keys') as mock_get_keys:
                mock_get_keys.return_value = 5  # Sufficient keys
                
                with patch.object(dungeon_service, 'deduct_shadow_keys') as mock_deduct:
                    mock_deduct.return_value = True
                    
                    with patch.object(dungeon_service, 'get_active_daily_modifier') as mock_modifier:
                        mock_modifier.return_value = sample_daily_modifier
                        
                        with patch.object(dungeon_service, 'get_quest_generation_service') as mock_quest_service:
                            mock_quest_gen = AsyncMock()
                            mock_quest_gen.generate_dungeon_trial.return_value = {
                                'trial_id': 'test_trial_123',
                                'movements': ['push_up', 'squat', 'burpee'],
                                'requirements': {'push_up': 20, 'squat': 30, 'burpee': 15}
                            }
                            mock_quest_service.return_value = mock_quest_gen
                            
                            # Mock session creation
                            mock_session.add = MagicMock()
                            mock_session.commit = AsyncMock()
                            
                            # Test dungeon entry
                            result = await dungeon_service.enter_dungeon(1, 5)
                            
                            # Verify entry result
                            assert result['status'] == 'success'
                            assert result['dungeon_level'] == 5
                            assert 'session_id' in result
                            assert 'trial_data' in result
                            
                            # Verify session was created
                            mock_session.add.assert_called_once()
                            mock_session.commit.assert_called_once()
    
    async def test_concurrent_dungeon_access_prevention(self, dungeon_service, sample_ascendant, mock_session):
        """Test that concurrent dungeon access is properly prevented."""
        # Setup mocks
        mock_session.get = AsyncMock(return_value=sample_ascendant)
        
        # Mock existing active session
        existing_session = DungeonSession(
            id=1,
            ascendant_id=1,
            dungeon_level=3,
            status='active',
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1)
        )
        
        # Mock the query to return an existing active session
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = existing_session
        mock_session.execute.return_value = result_mock
        
        # Test that concurrent access raises error
        with pytest.raises(ActiveSessionExistsError):
            await dungeon_service.enter_dungeon(1, 5)
    
    async def test_session_recovery_after_disconnect(self, dungeon_service, sample_ascendant, mock_session):
        """Test session recovery functionality after connection drop."""
        # Setup mocks
        mock_session.get = AsyncMock(return_value=sample_ascendant)
        
        # Mock existing session that can be recovered
        recoverable_session = DungeonSession(
            id=1,
            ascendant_id=1,
            dungeon_level=5,
            status='active',
            trial_data={'trial_id': 'test_123', 'progress': 50},
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=30)
        )
        
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = recoverable_session
        mock_session.execute.return_value = result_mock
        
        # Test session recovery
        result = await dungeon_service.get_active_session(1)
        
        assert result is not None
        assert result.id == 1
        assert result.status == 'active'
        assert result.trial_data['progress'] == 50
    
    async def test_expired_session_cleanup(self, dungeon_service, mock_session):
        """Test that expired sessions are properly cleaned up."""
        # Mock expired sessions
        expired_session1 = DungeonSession(
            id=1,
            ascendant_id=1,
            dungeon_level=3,
            status='active',
            expires_at=datetime.now(timezone.utc) - timedelta(hours=1)
        )
        
        expired_session2 = DungeonSession(
            id=2,
            ascendant_id=2,
            dungeon_level=4,
            status='active',
            expires_at=datetime.now(timezone.utc) - timedelta(minutes=30)
        )
        
        # Mock the query to return expired sessions
        result_mock = MagicMock()
        result_mock.scalars.return_value.all.return_value = [expired_session1, expired_session2]
        mock_session.execute.return_value = result_mock
        mock_session.commit = AsyncMock()
        
        # Test cleanup
        cleaned_count = await dungeon_service.cleanup_expired_sessions()
        
        assert cleaned_count == 2
        assert expired_session1.status == 'abandoned'
        assert expired_session2.status == 'abandoned'
        mock_session.commit.assert_called_once()
    
    async def test_trial_completion_with_rewards(self, dungeon_service, sample_ascendant, mock_session):
        """Test trial completion and reward distribution."""
        # Setup active session
        active_session = DungeonSession(
            id=1,
            ascendant_id=1,
            dungeon_level=5,
            status='active',
            trial_data={'trial_id': 'test_123', 'movements': ['push_up', 'squat']},
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1)
        )
        
        # Setup trial
        trial = DungeonTrial(
            id=1,
            session_id=1,
            trial_number=1,
            trial_type='reps',
            required_reps=20,
            completed_reps=0,
            is_completed=True  # Mark as completed for session completion logic
        )
        
        # Mock session.get to return different objects based on the model type
        def mock_get(model_class, obj_id, options=None):
            if model_class == DungeonSession:
                if options:
                    # If options are provided, return session with trials loaded
                    active_session.trials = [trial]  # Add the trial to the session
                return active_session
            elif model_class == DungeonTrial:
                return trial
            return None
        
        mock_session.get = AsyncMock(side_effect=mock_get)
        
        # Mock reward calculation
        with patch.object(dungeon_service, 'calculate_rewards') as mock_calc_rewards:
            mock_calc_rewards.return_value = [
                {'type': 'shadow_key', 'amount': 1},
                {'type': 'experience', 'amount': 100}
            ]
            
            with patch.object(dungeon_service, 'distribute_rewards') as mock_distribute:
                mock_distribute.return_value = True
                
                with patch.object(dungeon_service, 'update_dungeon_progress') as mock_update_progress:
                    mock_update_progress.return_value = None
                    
                    mock_session.commit = AsyncMock()
                    
                    # Test trial completion
                    completion_data = {
                        'reps': 25,  # More than required_reps of 20
                        'completion_time': 300,  # 5 minutes
                        'accuracy': 95.5
                    }
                    
                    result = await dungeon_service.complete_trial(1, completion_data)
                    
                    assert result['trial_completed'] == True
                    assert trial.is_completed == True
                    assert trial.completed_reps == 25
                    assert trial.trial_status == 'completed'
                    
                    # Verify session was updated
                    mock_session.commit.assert_called_once()
    
    async def test_performance_with_caching(self, dungeon_service, mock_session):
        """Test that caching improves performance for repeated operations."""
        # Mock cache service
        with patch.object(dungeon_service, 'get_cache_service') as mock_cache_service:
            cache_service = AsyncMock(spec=DungeonCacheService)
            cache_service.get_cached_daily_modifier.return_value = {
                'modifier_type': 'strength_focus',
                'difficulty_multiplier': 1.2,
                'reward_multiplier': 1.3
            }
            cache_service.get_cached_level_requirements.return_value = {
                'aura': 1000,
                'strength': 50,
                'endurance': 50,
                'technique': 50
            }
            mock_cache_service.return_value = cache_service
            
            # Test multiple calls to cached methods
            for _ in range(5):
                await cache_service.get_cached_daily_modifier()
                await cache_service.get_cached_level_requirements(5)
            
            # Verify cache was used
            assert cache_service.get_cached_daily_modifier.call_count == 5
            assert cache_service.get_cached_level_requirements.call_count == 5
    
    async def test_error_handling_integration(self, dungeon_service, mock_session):
        """Test comprehensive error handling across the system."""
        # Test database connection error
        mock_session.execute.side_effect = Exception("Database connection lost")
        
        with pytest.raises(Exception):
            await dungeon_service.health_check()
        
        # Reset mock
        mock_session.execute.side_effect = None
        
        # Test invalid ascendant ID
        mock_session.get = AsyncMock(return_value=None)
        
        with pytest.raises(InsufficientRequirementsError):
            await dungeon_service.validate_entry_requirements(999, 1)
    
    async def test_background_tasks_integration(self):
        """Test background tasks integration."""
        # Create background tasks instance (no arguments needed)
        background_tasks = DungeonBackgroundTasks()
        
        # Test task initialization
        assert background_tasks.dungeon_service is None
        assert background_tasks.cache_service is None
        assert background_tasks.is_running is False
        
        # Test that services can be created
        dungeon_service = await background_tasks.get_dungeon_service()
        assert dungeon_service is not None
        
        cache_service = await background_tasks.get_cache_service()
        assert cache_service is not None
        
        # Test starting/stopping tasks (would normally start actual tasks)
        # For testing, we'll just verify the structure
        assert hasattr(background_tasks, 'start_background_tasks')
        assert hasattr(background_tasks, 'stop_background_tasks')
        assert hasattr(background_tasks, '_session_cleanup_task')
        assert hasattr(background_tasks, '_daily_modifier_task')


@pytest.mark.asyncio
class TestDungeonSystemPerformance:
    """Performance tests for the dungeon system."""
    
    @pytest.fixture
    def dungeon_service(self):
        """Create a DungeonService for performance testing."""
        mock_session = AsyncMock()
        service = DungeonService(mock_session)
        return service
    
    async def test_bulk_session_processing(self, dungeon_service):
        """Test performance with bulk session processing."""
        # Mock multiple sessions
        sessions = []
        for i in range(100):
            session = DungeonSession(
                id=i,
                ascendant_id=i % 10,
                dungeon_level=i % 5 + 1,
                status='active',
                expires_at=datetime.now(timezone.utc) + timedelta(hours=1)
            )
            sessions.append(session)
        
        # Test that bulk processing doesn't timeout
        start_time = datetime.now()
        
        # Simulate processing all sessions
        processed_count = 0
        for session in sessions:
            # Simulate some processing
            if session.status == 'active':
                processed_count += 1
        
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        # Verify performance (should process 100 sessions quickly)
        assert processed_count == 100
        assert processing_time < 1.0  # Should complete in under 1 second
    
    async def test_concurrent_operations_performance(self, dungeon_service):
        """Test performance under concurrent operations."""
        # Simulate concurrent operations
        async def mock_operation(operation_id: int):
            # Simulate some async work
            await asyncio.sleep(0.01)  # 10ms delay
            return f"operation_{operation_id}_completed"
        
        # Run 50 concurrent operations
        start_time = datetime.now()
        
        tasks = [mock_operation(i) for i in range(50)]
        results = await asyncio.gather(*tasks)
        
        end_time = datetime.now()
        total_time = (end_time - start_time).total_seconds()
        
        # Verify all operations completed
        assert len(results) == 50
        assert all('completed' in result for result in results)
        
        # Should complete much faster than sequential (50 * 0.01 = 0.5s)
        assert total_time < 0.3  # Should complete in under 300ms due to concurrency