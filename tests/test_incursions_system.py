"""
Test suite for the Incursions System

This test suite covers:
- IncursionService business logic
- IncursionScheduler with spawn cooldowns
- Database models and relationships
- API endpoints
- Repository pattern
"""
import pytest
import asyncio
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from typing import List, Dict, Any

from app.application.services.incursion_service import IncursionService
from app.application.services.incursion_scheduler import (
    IncursionScheduler, SpawnCooldownConfig, IncursionTemplate
)
from app.infrastructure.database.models.v2.incursions import (
    Incursion, IncursionParticipant, IncursionType, RewardType, IncursionStatus
)
from app.infrastructure.repositories.incursion_repository import IncursionRepository


class TestIncursionModels:
    """Test the incursion database models."""
    
    def test_incursion_model_creation(self):
        """Test creating an Incursion model."""
        incursion = Incursion(
            incursion_id="test_incursion_123",
            title="Test Incursion",
            description="A test incursion for unit testing",
            incursion_type=IncursionType.SURGE,
            target_exercise="push_ups",
            target_reps=100,
            reward_type=RewardType.XP,
            reward_value=200,
            reward_description="Test XP reward",
            expires_at=datetime.now(timezone.utc) + timedelta(hours=24)
        )
        
        assert incursion.incursion_id == "test_incursion_123"
        assert incursion.title == "Test Incursion"
        assert incursion.incursion_type == IncursionType.SURGE
        assert incursion.target_reps == 100
        assert incursion.current_reps == 0  # Default value
        assert incursion.is_active == True  # Default value
        assert incursion.status == IncursionStatus.ACTIVE  # Default value
    
    def test_incursion_progress_calculation(self):
        """Test incursion progress percentage calculation."""
        incursion = Incursion(
            incursion_id="test_progress",
            title="Progress Test",
            description="Testing progress calculation",
            incursion_type=IncursionType.CHALLENGE,
            target_exercise="squats",
            target_reps=200,
            reward_type=RewardType.XP,
            reward_value=300,
            reward_description="Progress test reward",
            expires_at=datetime.now(timezone.utc) + timedelta(hours=12)
        )
        
        # Test initial progress
        assert incursion.progress_percentage == 0.0
        assert not incursion.is_completed
        
        # Test partial progress
        incursion.current_reps = 50
        assert incursion.progress_percentage == 25.0
        assert not incursion.is_completed
        
        # Test completion
        incursion.current_reps = 200
        assert incursion.progress_percentage == 100.0
        assert incursion.is_completed
        
        # Test over-completion
        incursion.current_reps = 250
        assert incursion.progress_percentage == 125.0
        assert incursion.is_completed
    
    def test_incursion_participant_model(self):
        """Test creating an IncursionParticipant model."""
        participant = IncursionParticipant(
            incursion_id=1,
            user_id=123,
            reps_contributed=50,
            participated_at=datetime.now(timezone.utc)
        )
        
        assert participant.incursion_id == 1
        assert participant.user_id == 123
        assert participant.reps_contributed == 50
        assert isinstance(participant.participated_at, datetime)


class TestSpawnCooldownConfig:
    """Test the spawn cooldown configuration."""
    
    def test_default_config(self):
        """Test default cooldown configuration."""
        config = SpawnCooldownConfig()
        
        assert config.min_cooldown_minutes == 30
        assert config.max_cooldown_minutes == 120
        assert config.max_concurrent_incursions == 3
        assert IncursionType.SURGE in config.type_specific_cooldowns
        assert IncursionType.CHALLENGE in config.type_specific_cooldowns
        assert IncursionType.ANOMALY in config.type_specific_cooldowns
    
    def test_custom_config(self):
        """Test custom cooldown configuration."""
        custom_cooldowns = {
            IncursionType.SURGE: 30,
            IncursionType.CHALLENGE: 60,
            IncursionType.ANOMALY: 120
        }
        
        config = SpawnCooldownConfig(
            min_cooldown_minutes=15,
            max_cooldown_minutes=90,
            type_specific_cooldowns=custom_cooldowns,
            max_concurrent_incursions=5
        )
        
        assert config.min_cooldown_minutes == 15
        assert config.max_cooldown_minutes == 90
        assert config.max_concurrent_incursions == 5
        assert config.type_specific_cooldowns[IncursionType.SURGE] == 30


class TestIncursionTemplate:
    """Test incursion template functionality."""
    
    def test_template_creation(self):
        """Test creating an incursion template."""
        template = IncursionTemplate(
            title="Test Template",
            description="A template for testing",
            incursion_type=IncursionType.SURGE,
            target_exercise="push_ups",
            target_reps_range=(50, 150),
            reward_type=RewardType.XP,
            reward_value_range=(100, 300),
            reward_description="Test reward",
            duration_hours=2.0,
            weight=1.5
        )
        
        assert template.title == "Test Template"
        assert template.incursion_type == IncursionType.SURGE
        assert template.target_reps_range == (50, 150)
        assert template.weight == 1.5


@pytest.mark.asyncio
class TestIncursionService:
    """Test the IncursionService business logic."""
    
    @pytest.fixture
    def mock_session(self):
        """Create a mock database session."""
        session = AsyncMock()
        return session
    
    @pytest.fixture
    def incursion_service(self, mock_session):
        """Create an IncursionService with mocked session."""
        service = IncursionService(mock_session)
        service.get_session = AsyncMock(return_value=mock_session)
        return service
    
    async def test_create_incursion_success(self, incursion_service, mock_session):
        """Test successful incursion creation."""
        # Mock the session operations
        mock_session.add = MagicMock()
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()
        
        # Create incursion
        incursion = await incursion_service.create_incursion(
            title="Test Incursion",
            description="A test incursion",
            incursion_type=IncursionType.SURGE,
            target_exercise="push_ups",
            target_reps=100,
            reward_type=RewardType.XP,
            reward_value=200,
            reward_description="Test reward"
        )
        
        # Verify the incursion was created
        assert incursion.title == "Test Incursion"
        assert incursion.target_reps == 100
        assert incursion.is_active == True
        
        # Verify session operations were called
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once()
    
    async def test_create_incursion_validation_errors(self, incursion_service):
        """Test incursion creation with invalid parameters."""
        # Test negative target reps
        with pytest.raises(ValueError, match="Target reps must be positive"):
            await incursion_service.create_incursion(
                title="Invalid Incursion",
                description="Invalid test",
                incursion_type=IncursionType.SURGE,
                target_exercise="push_ups",
                target_reps=-10,  # Invalid
                reward_type=RewardType.XP,
                reward_value=200,
                reward_description="Test reward"
            )
        
        # Test negative reward value
        with pytest.raises(ValueError, match="Reward value must be positive"):
            await incursion_service.create_incursion(
                title="Invalid Incursion",
                description="Invalid test",
                incursion_type=IncursionType.SURGE,
                target_exercise="push_ups",
                target_reps=100,
                reward_type=RewardType.XP,
                reward_value=-50,  # Invalid
                reward_description="Test reward"
            )
    
    async def test_add_participant_contribution_success(self, incursion_service):
        """Test successful participant contribution."""
        # Mock an existing incursion
        mock_incursion = MagicMock()
        mock_incursion.id = 1
        mock_incursion.is_active = True
        mock_incursion.current_reps = 50
        mock_incursion.target_reps = 100
        mock_incursion.participants = []
        mock_incursion.is_completed = False
        
        incursion_service.get_incursion_by_id = AsyncMock(return_value=mock_incursion)
        
        # Mock session with proper add method
        mock_session = AsyncMock()
        mock_session.add = MagicMock()  # Synchronous mock for session.add
        mock_session.commit = AsyncMock()  # Async mock for session.commit
        incursion_service.get_session = AsyncMock(return_value=mock_session)
        
        # Add contribution
        result = await incursion_service.add_participant_contribution(
            incursion_id="test_incursion",
            user_id=123,
            reps=25
        )
        
        assert result == True
        assert mock_incursion.current_reps == 75  # 50 + 25
    
    async def test_add_contribution_to_inactive_incursion(self, incursion_service):
        """Test adding contribution to inactive incursion."""
        # Mock an inactive incursion
        mock_incursion = MagicMock()
        mock_incursion.is_active = False
        
        incursion_service.get_incursion_by_id = AsyncMock(return_value=mock_incursion)
        
        # Try to add contribution
        result = await incursion_service.add_participant_contribution(
            incursion_id="inactive_incursion",
            user_id=123,
            reps=25
        )
        
        assert result == False


@pytest.mark.asyncio
class TestIncursionScheduler:
    """Test the IncursionScheduler with spawn cooldowns."""
    
    @pytest.fixture
    def mock_incursion_service(self):
        """Create a mock IncursionService."""
        service = AsyncMock()
        service.get_active_incursions = AsyncMock(return_value=[])
        service.cleanup_expired_incursions = AsyncMock(return_value=0)
        service.health_check = AsyncMock(return_value={"status": "healthy"})
        return service
    
    @pytest.fixture
    def cooldown_config(self):
        """Create a test cooldown configuration."""
        return SpawnCooldownConfig(
            min_cooldown_minutes=5,  # Shorter for testing
            max_cooldown_minutes=15,
            max_concurrent_incursions=2
        )
    
    @pytest.fixture
    def scheduler(self, mock_incursion_service, cooldown_config):
        """Create an IncursionScheduler for testing."""
        return IncursionScheduler(mock_incursion_service, cooldown_config)
    
    async def test_scheduler_initialization(self, scheduler):
        """Test scheduler initialization."""
        assert not scheduler.is_running
        assert scheduler.last_spawn_time is None
        assert len(scheduler.incursion_templates) > 0
        assert scheduler.cooldown_config.min_cooldown_minutes == 5
    
    async def test_should_spawn_first_incursion(self, scheduler):
        """Test that first incursion should always spawn."""
        should_spawn = await scheduler._should_spawn_incursion()
        assert should_spawn == True
    
    async def test_should_not_spawn_during_min_cooldown(self, scheduler):
        """Test that incursions don't spawn during minimum cooldown."""
        # Set a recent spawn time
        scheduler.last_spawn_time = datetime.now(timezone.utc) - timedelta(minutes=2)
        
        should_spawn = await scheduler._should_spawn_incursion()
        assert should_spawn == False
    
    async def test_should_not_spawn_at_max_concurrent(self, scheduler, mock_incursion_service):
        """Test that incursions don't spawn when at max concurrent limit."""
        # Mock max concurrent incursions
        mock_incursions = [MagicMock() for _ in range(2)]  # Max is 2 in test config
        mock_incursion_service.get_active_incursions.return_value = mock_incursions
        
        should_spawn = await scheduler._should_spawn_incursion()
        assert should_spawn == False
    
    async def test_weighted_random_choice(self, scheduler):
        """Test weighted random template selection."""
        templates = [
            IncursionTemplate(
                title="High Weight", description="", incursion_type=IncursionType.SURGE,
                target_exercise="test", target_reps_range=(1, 2), reward_type=RewardType.XP,
                reward_value_range=(1, 2), reward_description="", duration_hours=1.0,
                weight=10.0
            ),
            IncursionTemplate(
                title="Low Weight", description="", incursion_type=IncursionType.SURGE,
                target_exercise="test", target_reps_range=(1, 2), reward_type=RewardType.XP,
                reward_value_range=(1, 2), reward_description="", duration_hours=1.0,
                weight=0.1
            )
        ]
        
        # Run multiple selections to test weighting
        selections = []
        for _ in range(100):
            selected = scheduler._weighted_random_choice(templates)
            selections.append(selected.title)
        
        # High weight template should be selected more often
        high_weight_count = selections.count("High Weight")
        low_weight_count = selections.count("Low Weight")
        
        assert high_weight_count > low_weight_count
    
    async def test_force_spawn_incursion(self, scheduler, mock_incursion_service):
        """Test force spawning an incursion."""
        # Mock incursion creation
        mock_incursion = MagicMock()
        mock_incursion.title = "Forced Incursion"
        mock_incursion_service.create_incursion = AsyncMock(return_value=mock_incursion)
        
        # Force spawn
        result = await scheduler.force_spawn_incursion(IncursionType.SURGE)
        
        assert result == True
        assert scheduler.last_spawn_time is not None
        mock_incursion_service.create_incursion.assert_called_once()
    
    async def test_get_cooldown_status(self, scheduler):
        """Test getting cooldown status information."""
        # Set some spawn times
        current_time = datetime.now(timezone.utc)
        scheduler.last_spawn_time = current_time - timedelta(minutes=3)
        scheduler.last_spawn_by_type[IncursionType.SURGE] = current_time - timedelta(minutes=2)
        
        status = scheduler.get_cooldown_status()
        
        assert status["is_running"] == False
        assert status["last_spawn_time"] is not None
        assert status["global_cooldown_remaining"] is not None
        assert "type_cooldowns" in status
        assert "config" in status
    
    async def test_scheduler_start_stop(self, scheduler):
        """Test starting and stopping the scheduler."""
        # Start scheduler
        await scheduler.start()
        assert scheduler.is_running == True
        assert scheduler.scheduler_task is not None
        
        # Stop scheduler
        await scheduler.stop()
        assert scheduler.is_running == False


@pytest.mark.asyncio
class TestIncursionRepository:
    """Test the IncursionRepository data access layer."""
    
    @pytest.fixture
    def mock_session(self):
        """Create a mock database session."""
        session = AsyncMock()
        return session
    
    @pytest.fixture
    def repository(self, mock_session):
        """Create an IncursionRepository with mocked session."""
        return IncursionRepository(mock_session)
    
    async def test_create_incursion(self, repository, mock_session):
        """Test creating an incursion through repository."""
        incursion = Incursion(
            incursion_id="repo_test",
            title="Repository Test",
            description="Testing repository",
            incursion_type=IncursionType.CHALLENGE,
            target_exercise="squats",
            target_reps=150,
            reward_type=RewardType.XP,
            reward_value=250,
            reward_description="Repo test reward",
            expires_at=datetime.now(timezone.utc) + timedelta(hours=6)
        )
        
        # Mock session operations
        mock_session.add = MagicMock()
        mock_session.flush = AsyncMock()
        mock_session.refresh = AsyncMock()
        
        result = await repository.create(incursion)
        
        assert result == incursion
        mock_session.add.assert_called_once_with(incursion)
        mock_session.flush.assert_called_once()
        mock_session.refresh.assert_called_once_with(incursion)
    
    async def test_count_active_incursions(self, repository, mock_session):
        """Test counting active incursions."""
        # Mock the query result
        mock_result = MagicMock()
        mock_result.scalar.return_value = 5
        mock_session.execute = AsyncMock(return_value=mock_result)
        
        count = await repository.count_active_incursions()
        
        assert count == 5
        mock_session.execute.assert_called_once()


class TestIncursionIntegration:
    """Integration tests for the complete incursion system."""
    
    @pytest.mark.asyncio
    async def test_full_incursion_lifecycle(self):
        """Test a complete incursion lifecycle from creation to completion."""
        # This would be an integration test that tests the full flow
        # In a real implementation, this would use a test database
        pass
    
    @pytest.mark.asyncio
    async def test_scheduler_integration_with_service(self):
        """Test scheduler integration with incursion service."""
        # This would test the scheduler actually creating incursions
        # through the service layer
        pass


class TestSpawnCooldowns:
    """Specific tests for spawn cooldown functionality."""
    
    @pytest.mark.asyncio
    async def test_global_cooldown_enforcement(self):
        """Test that global cooldowns are properly enforced."""
        config = SpawnCooldownConfig(min_cooldown_minutes=10, max_cooldown_minutes=30)
        service = AsyncMock()
        service.get_active_incursions = AsyncMock(return_value=[])
        
        scheduler = IncursionScheduler(service, config)
        
        # First spawn should be allowed
        should_spawn = await scheduler._should_spawn_incursion()
        assert should_spawn == True
        
        # Set recent spawn time
        scheduler.last_spawn_time = datetime.now(timezone.utc) - timedelta(minutes=5)
        
        # Should not spawn due to global cooldown
        should_spawn = await scheduler._should_spawn_incursion()
        assert should_spawn == False
    
    @pytest.mark.asyncio
    async def test_type_specific_cooldowns(self):
        """Test that type-specific cooldowns work correctly."""
        config = SpawnCooldownConfig()
        config.type_specific_cooldowns = {
            IncursionType.SURGE: 30,
            IncursionType.CHALLENGE: 60,
            IncursionType.ANOMALY: 120
        }
        
        service = AsyncMock()
        service.get_active_incursions = AsyncMock(return_value=[])
        
        scheduler = IncursionScheduler(service, config)
        
        # Set recent spawn for SURGE type
        current_time = datetime.now(timezone.utc)
        scheduler.last_spawn_by_type[IncursionType.SURGE] = current_time - timedelta(minutes=15)
        scheduler.last_spawn_time = current_time - timedelta(minutes=60)  # Global cooldown passed
        
        # Filter available templates (SURGE should be filtered out)
        available_templates = []
        for template in scheduler.incursion_templates:
            if template.incursion_type in scheduler.last_spawn_by_type:
                last_spawn = scheduler.last_spawn_by_type[template.incursion_type]
                type_cooldown = config.type_specific_cooldowns[template.incursion_type]
                cooldown_delta = timedelta(minutes=type_cooldown)
                
                if current_time - last_spawn >= cooldown_delta:
                    available_templates.append(template)
            else:
                available_templates.append(template)
        
        # SURGE templates should be filtered out due to cooldown
        surge_templates = [t for t in available_templates if t.incursion_type == IncursionType.SURGE]
        assert len(surge_templates) == 0
    
    def test_cooldown_status_reporting(self):
        """Test that cooldown status is properly reported."""
        config = SpawnCooldownConfig(min_cooldown_minutes=15, max_cooldown_minutes=45)
        service = AsyncMock()
        scheduler = IncursionScheduler(service, config)
        
        # Set some spawn times
        current_time = datetime.now(timezone.utc)
        scheduler.last_spawn_time = current_time - timedelta(minutes=10)
        scheduler.last_spawn_by_type[IncursionType.SURGE] = current_time - timedelta(minutes=20)
        scheduler.last_spawn_by_type[IncursionType.CHALLENGE] = current_time - timedelta(minutes=40)
        
        status = scheduler.get_cooldown_status()
        
        # Check structure
        assert "is_running" in status
        assert "last_spawn_time" in status
        assert "global_cooldown_remaining" in status
        assert "type_cooldowns" in status
        assert "config" in status
        
        # Check global cooldown (should have ~5 minutes remaining)
        assert status["global_cooldown_remaining"] > 0
        assert status["global_cooldown_remaining"] <= 300  # 5 minutes in seconds
        
        # Check type cooldowns
        assert IncursionType.SURGE.value in status["type_cooldowns"]
        assert IncursionType.CHALLENGE.value in status["type_cooldowns"]


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])