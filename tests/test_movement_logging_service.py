"""
Tests for the MovementLoggingService.

This module contains comprehensive tests for the movement logging functionality,
including XP calculation, progression integration, and error handling.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.movement_logging_service import MovementLoggingService, MovementLogResult
from app.application.services.progression_service import ProgressionResult
from app.infrastructure.database.models.v2.movements import Movement


class TestMovementLoggingService:
    """Test suite for MovementLoggingService."""
    
    @pytest.fixture
    def mock_session(self):
        """Create a mock database session."""
        session = AsyncMock(spec=AsyncSession)
        return session
    
    @pytest.fixture
    def movement_service(self, mock_session):
        """Create a MovementLoggingService instance with mocked session."""
        return MovementLoggingService(session=mock_session)
    
    @pytest.fixture
    def sample_movement(self):
        """Create a sample movement for testing."""
        movement = Movement()
        movement.id = 1
        movement.name = "Push-ups"
        movement.xp_per_rep = 5
        movement.stat_reward_type = "STR"
        movement.node_id = "pushup_node"
        return movement
    
    @pytest.fixture
    def mock_progression_service(self):
        """Create a mock ProgressionService."""
        service = AsyncMock()
        return service
    
    @pytest.mark.asyncio
    async def test_log_movement_success(self, movement_service, mock_session, sample_movement, mock_progression_service):
        """Test successful movement logging with XP calculation and stat rewards."""
        # Setup
        user_id = 1
        reps = 10
        session_id = "test_session_123"
        
        # Mock database query for movement retrieval
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_movement
        mock_session.execute.return_value = mock_result
        
        # Mock progression service
        movement_service._progression_service = mock_progression_service
        
        # Mock progression results
        global_result = ProgressionResult()
        global_result.level_changes = {}
        global_result.previous_aura = 1000
        global_result.new_aura = 1025
        
        strength_result = ProgressionResult()
        strength_result.level_changes = {"strength": {"new": 5, "gained": 2}}
        strength_result.previous_aura = 1000
        strength_result.new_aura = 1025
        
        # Mock stat rewards result
        stat_rewards_result = ProgressionResult()
        stat_rewards_result.stat_rewards_awarded = {"str_reward": 5, "end_reward": 1, "tech_reward": 0}
        stat_rewards_result.level_changes = {"strength": {"new": 5, "gained": 2}}
        stat_rewards_result.previous_aura = 1025
        stat_rewards_result.new_aura = 1030
        
        mock_progression_service.add_xp.return_value = global_result
        mock_progression_service.add_stat_rewards.return_value = stat_rewards_result
        
        # Mock transaction execution
        async def mock_transaction(func):
            return await func(mock_session)
        
        movement_service.execute_in_transaction = mock_transaction
        
        # Execute
        result = await movement_service.log_movement(user_id, sample_movement.id, reps, session_id)
        
        # Verify
        assert isinstance(result, MovementLogResult)
        assert result.user_id == user_id
        assert result.movement_id == sample_movement.id
        assert result.movement_name == sample_movement.name
        assert result.reps_logged == reps
        assert result.session_id == session_id
        
        # Verify XP calculations
        assert result.xp_earned["global"] == 50  # 5 * 10
        assert result.xp_earned["strength"] == 37  # 50 * 0.75
        
        # Verify stat rewards
        assert result.stat_rewards == {"str_reward": 5, "end_reward": 1, "tech_reward": 0}
        
        # Verify progression service calls
        assert mock_progression_service.add_xp.call_count == 1  # Only global XP now
        assert mock_progression_service.add_stat_rewards.call_count == 1
        
        # Verify level-ups
        assert len(result.level_ups) == 1
        assert result.level_ups[0]["type"] == "strength"
        assert result.level_ups[0]["new_level"] == 5
        assert result.level_ups[0]["points_earned"] == 2
        
        # Verify aura update
        assert result.aura_update["previous_aura"] == 1025
        assert result.aura_update["new_aura"] == 1030
        assert result.aura_update["change"] == 5
    
    @pytest.mark.asyncio
    async def test_log_movement_invalid_reps(self, movement_service):
        """Test movement logging with invalid reps."""
        with pytest.raises(ValueError, match="Reps must be positive"):
            await movement_service.log_movement(1, 1, 0)
        
        with pytest.raises(ValueError, match="Reps must be positive"):
            await movement_service.log_movement(1, 1, -5)
    
    @pytest.mark.asyncio
    async def test_log_movement_invalid_movement_id(self, movement_service):
        """Test movement logging with invalid movement ID."""
        with pytest.raises(ValueError, match="Movement ID must be positive"):
            await movement_service.log_movement(1, 0, 10)
        
        with pytest.raises(ValueError, match="Movement ID must be positive"):
            await movement_service.log_movement(1, -1, 10)
    
    @pytest.mark.asyncio
    async def test_log_movement_not_found(self, movement_service, mock_session):
        """Test movement logging when movement is not found."""
        # Setup
        user_id = 1
        movement_id = 999
        reps = 10
        session_id = "test-session-123"
        
        # Mock database query to return None (movement not found)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result
        
        # Mock transaction execution
        async def mock_transaction(func):
            return await func(mock_session)
        
        movement_service.execute_in_transaction = mock_transaction
        
        # Execute and verify
        with pytest.raises(Exception, match=r"Movement with ID \d+ not found"):
            await movement_service.log_movement(user_id, movement_id, reps, session_id)
    
    @pytest.mark.asyncio
    async def test_calculate_movement_xp_strength(self, movement_service, sample_movement):
        """Test XP and stat rewards calculation for strength movement."""
        sample_movement.stat_reward_type = "STR"
        sample_movement.xp_per_rep = 5
        
        result = await movement_service._calculate_movement_xp(sample_movement, 10)
        
        # Verify XP calculations
        assert result["global"] == 50  # 5 * 10
        assert result["strength"] == 37  # 50 * 0.75
        assert "endurance" not in result
        assert "technique" not in result
        
        # Verify stat rewards calculations
        assert result["str_reward"] == 5  # 0.5 * 10
        assert result["end_reward"] == 1  # 0.25 * 0.5 * 10 = 1.25, int() = 1
        assert result["tech_reward"] == 0  # 0.16 * 0.5 * 10 = 0.8, int() = 0
    
    @pytest.mark.asyncio
    async def test_calculate_movement_xp_endurance(self, movement_service, sample_movement):
        """Test XP and stat rewards calculation for endurance movement."""
        sample_movement.stat_reward_type = "END"
        sample_movement.xp_per_rep = 3
        
        result = await movement_service._calculate_movement_xp(sample_movement, 15)
        
        # Verify XP calculations
        assert result["global"] == 45  # 3 * 15
        assert result["endurance"] == 33  # 45 * 0.75
        assert "strength" not in result
        assert "technique" not in result
        
        # Verify stat rewards calculations
        assert result["end_reward"] == 7  # 0.5 * 15 = 7.5, int() = 7
        assert result["str_reward"] == 1  # 0.25 * 0.5 * 15 = 1.875, int() = 1
        assert result["tech_reward"] == 1  # 0.16 * 0.5 * 15 = 1.2, int() = 1
    
    @pytest.mark.asyncio
    async def test_calculate_movement_xp_technique(self, movement_service, sample_movement):
        """Test XP and stat rewards calculation for technique movement."""
        sample_movement.stat_reward_type = "TECH"
        sample_movement.xp_per_rep = 8
        
        result = await movement_service._calculate_movement_xp(sample_movement, 5)
        
        # Verify XP calculations
        assert result["global"] == 40  # 8 * 5
        assert result["technique"] == 30  # 40 * 0.75
        assert "strength" not in result
        assert "endurance" not in result
        
        # Verify stat rewards calculations
        assert result["tech_reward"] == 2  # 0.5 * 5 = 2.5, int() = 2
        assert result["str_reward"] == 0  # 0.25 * 0.5 * 5 = 0.625, int() = 0
        assert result["end_reward"] == 0  # 0.16 * 0.5 * 5 = 0.4, int() = 0
    
    @pytest.mark.asyncio
    async def test_calculate_movement_xp_unknown_stat(self, movement_service, sample_movement):
        """Test XP and stat rewards calculation for movement with unknown stat type."""
        sample_movement.stat_reward_type = "UNKNOWN"
        sample_movement.xp_per_rep = 4
        
        result = await movement_service._calculate_movement_xp(sample_movement, 12)
        
        # Verify XP calculations
        assert result["global"] == 48  # 4 * 12
        assert len([k for k in result.keys() if k in ["strength", "endurance", "technique"]]) == 0  # No stat-specific XP
        
        # Verify stat rewards calculations (should default to balanced distribution)
        assert result["str_reward"] == 6  # 0.5 * 12
        assert result["end_reward"] == 1  # 0.25 * 0.5 * 12 = 1.5, int() = 1
        assert result["tech_reward"] == 0  # 0.16 * 0.5 * 12 = 0.96, int() = 0 (rounded down)
    
    @pytest.mark.asyncio
    async def test_get_movement_by_id_success(self, movement_service, mock_session, sample_movement):
        """Test successful movement retrieval by ID."""
        # Setup
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_movement
        mock_session.execute.return_value = mock_result
        movement_service.get_session = AsyncMock(return_value=mock_session)
        
        # Execute
        result = await movement_service.get_movement_by_id(sample_movement.id)
        
        # Verify
        assert result is not None
        assert result["id"] == sample_movement.id
        assert result["name"] == sample_movement.name
        assert result["xp_per_rep"] == sample_movement.xp_per_rep
        assert result["stat_reward_type"] == sample_movement.stat_reward_type
        assert result["node_id"] == sample_movement.node_id
    
    @pytest.mark.asyncio
    async def test_get_movement_by_id_not_found(self, movement_service, mock_session):
        """Test movement retrieval when movement is not found."""
        # Setup
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result
        movement_service.get_session = AsyncMock(return_value=mock_session)
        
        # Execute
        result = await movement_service.get_movement_by_id(999)
        
        # Verify
        assert result is None
    
    @pytest.mark.asyncio
    async def test_process_progression_results_multiple_level_ups(self, movement_service):
        """Test processing progression results with multiple level-ups."""
        # Setup
        result = MovementLogResult()
        result.user_id = 1
        
        global_result = ProgressionResult()
        global_result.level_changes = {"global": {"new": 10, "gained": 1}}
        global_result.previous_aura = 1000
        global_result.new_aura = 1050
        
        strength_result = ProgressionResult()
        strength_result.level_changes = {"strength": {"new": 5, "gained": 2}}
        strength_result.previous_aura = 1000
        strength_result.new_aura = 1050
        
        progression_results = [
            ("global", global_result),
            ("strength", strength_result)
        ]
        
        # Execute
        await movement_service._process_progression_results(progression_results, result)
        
        # Verify
        assert len(result.level_ups) == 2
        
        # Check global level-up
        global_levelup = next(lu for lu in result.level_ups if lu["type"] == "global")
        assert global_levelup["new_level"] == 10
        assert global_levelup["points_earned"] == 1
        
        # Check strength level-up
        strength_levelup = next(lu for lu in result.level_ups if lu["type"] == "strength")
        assert strength_levelup["new_level"] == 5
        assert strength_levelup["points_earned"] == 2
        
        # Check aura update
        assert result.aura_update["previous_aura"] == 1000
        assert result.aura_update["new_aura"] == 1050
        assert result.aura_update["change"] == 50
    
    @pytest.mark.asyncio
    async def test_process_progression_results_no_level_ups(self, movement_service):
        """Test processing progression results with no level-ups."""
        # Setup
        result = MovementLogResult()
        result.user_id = 1
        
        global_result = ProgressionResult()
        global_result.level_changes = {}
        global_result.previous_aura = 1000
        global_result.new_aura = 1000  # No aura change
        
        progression_results = [("global", global_result)]
        
        # Execute
        await movement_service._process_progression_results(progression_results, result)
        
        # Verify
        assert len(result.level_ups) == 0
        assert result.aura_update == {}
    
    @pytest.mark.asyncio
    async def test_health_check_success(self, movement_service, mock_session, mock_progression_service):
        """Test successful health check."""
        # Setup
        mock_movements = [MagicMock(), MagicMock(), MagicMock()]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_movements
        mock_session.execute.return_value = mock_result
        movement_service.get_session = AsyncMock(return_value=mock_session)
        
        movement_service.get_progression_service = AsyncMock(return_value=mock_progression_service)
        mock_progression_service.health_check = AsyncMock(return_value={"status": "healthy"})
        
        # Execute
        result = await movement_service.health_check()
        
        # Verify
        assert result["service"] == "MovementLoggingService"
        assert result["status"] == "healthy"
        assert result["database_connection"] == "ok"
        assert result["movements_count"] == 3
        assert result["progression_service_status"] == "healthy"
    
    @pytest.mark.asyncio
    async def test_health_check_failure(self, movement_service, mock_session):
        """Test health check when database is unavailable."""
        # Setup
        mock_session.execute.side_effect = Exception("Database connection failed")
        movement_service.get_session = AsyncMock(return_value=mock_session)
        movement_service.handle_service_error = MagicMock()
        
        # Execute
        result = await movement_service.health_check()
        
        # Verify
        assert result["service"] == "MovementLoggingService"
        assert result["status"] == "unhealthy"
        assert "error" in result
    
    @pytest.mark.asyncio
    async def test_movement_log_result_to_dict(self):
        """Test MovementLogResult to_dict conversion."""
        # Setup
        result = MovementLogResult()
        result.movement_id = 1
        result.movement_name = "Push-ups"
        result.reps_logged = 10
        result.xp_earned = {"global": 50, "strength": 37}
        result.level_ups = [{"type": "strength", "new_level": 5, "points_earned": 2}]
        result.aura_update = {"previous_aura": 1000, "new_aura": 1025, "change": 25}
        result.session_id = "test_session"
        
        # Execute
        dict_result = result.to_dict()
        
        # Verify
        assert dict_result["movement"]["id"] == 1
        assert dict_result["movement"]["name"] == "Push-ups"
        assert dict_result["reps_logged"] == 10
        assert dict_result["xp_earned"] == {"global": 50, "strength": 37}
        assert dict_result["level_ups"] == [{"type": "strength", "new_level": 5, "points_earned": 2}]
        assert dict_result["aura_update"] == {"previous_aura": 1000, "new_aura": 1025, "change": 25}
        assert dict_result["session_id"] == "test_session"


class TestMovementLogResult:
    """Test suite for MovementLogResult class."""
    
    def test_initialization(self):
        """Test MovementLogResult initialization."""
        result = MovementLogResult()
        
        assert result.user_id is None
        assert result.movement_id == 0
        assert result.movement_name == ""
        assert result.reps_logged == 0
        assert result.xp_earned == {}
        assert result.level_ups == []
        assert result.aura_update == {}
        assert result.session_id is None
    
    def test_to_dict_empty(self):
        """Test to_dict with empty result."""
        result = MovementLogResult()
        dict_result = result.to_dict()
        
        expected = {
            "movement": {"id": 0, "name": ""},
            "reps_logged": 0,
            "xp_earned": {},
            "level_ups": [],
            "aura_update": {},
            "session_id": None,
            "stat_rewards": {}
        }
        
        assert dict_result == expected