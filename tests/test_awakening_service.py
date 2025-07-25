"""Unit tests for AwakeningService."""
import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.awakening_service import AwakeningService, ValidationError, NotFoundError
from app.application.services.progression_service import ProgressionService
from app.infrastructure.database.models.v2.awakening import AwakeningSession, AwakeningQuest, AwakeningReward, UserAwakeningProgress
from app.infrastructure.database.models.v2.ascendants import Ascendant


@pytest.fixture
def mock_session():
    """Mock database session."""
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def mock_progression_service():
    """Mock progression service."""
    return AsyncMock(spec=ProgressionService)


@pytest.fixture
def awakening_service():
    """Create AwakeningService instance with mocked dependencies"""
    db_session = AsyncMock(spec=AsyncSession)
    progression_service = AsyncMock(spec=ProgressionService)
    service = AwakeningService(db_session, progression_service)
    return service


class TestAwakeningService:
    """Test cases for AwakeningService."""

    @pytest.mark.asyncio
    async def test_get_daily_session_exists(self, awakening_service):
        """Test getting an existing daily session"""
        user_id = 1
        session_date = datetime.now(timezone.utc).date()
        
        # Mock existing session
        mock_session = MagicMock(spec=AwakeningSession)
        mock_session.id = 1
        mock_session.user_id = user_id
        mock_session.session_date = session_date
        
        # Mock database query
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_session
        awakening_service.db_session.execute.return_value = mock_result
        
        result = await awakening_service.get_daily_session(user_id, session_date)
        
        assert result == mock_session
        awakening_service.db_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_daily_session_not_exists(self, awakening_service):
        """Test getting a non-existent daily session"""
        user_id = 1
        session_date = datetime.now(timezone.utc).date()
        
        # Mock no session found
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        awakening_service.db_session.execute.return_value = mock_result
        
        result = await awakening_service.get_daily_session(user_id, session_date)
        
        assert result is None
        awakening_service.db_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_daily_session(self, awakening_service):
        """Test creating a new daily session"""
        user_id = 1
        readiness_level = 5
        session_date = datetime.now(timezone.utc).date()
        
        # Mock no existing session
        awakening_service.get_daily_session = AsyncMock(return_value=None)
        
        # Mock user progress creation
        mock_progress = MagicMock(spec=UserAwakeningProgress)
        mock_progress.current_streak = 0
        mock_progress.longest_streak = 0
        mock_progress.total_sessions_completed = 0
        mock_progress.total_quests_completed = 0
        mock_progress.total_xp_earned = 0
        mock_progress.total_aura_earned = 0
        mock_progress.total_shadow_keys_earned = 0
        mock_progress.awakening_streak = 0  # Add missing attribute
        
        mock_progress_result = MagicMock()
        mock_progress_result.scalar_one_or_none.return_value = mock_progress
        awakening_service.db_session.execute.return_value = mock_progress_result
        
        # Mock quest generation
        mock_quest_data = [
            {
                'quest_type': 'movement_reps',
                'target_movement_id': 1,
                'target_reps': 10,
                'difficulty_level': 'normal'
            }
        ]
        awakening_service.quest_generation_service.generate_daily_quests = AsyncMock(return_value=mock_quest_data)
        
        # Mock cache service
        awakening_service.cache_service.get_user_progression = AsyncMock(return_value=None)
        awakening_service.cache_service.cache_user_progression = AsyncMock()
        awakening_service.cache_service.cache_daily_session = AsyncMock()
        
        # Mock _format_session_for_api
        mock_session_data = {'session_id': 1, 'quests': []}
        awakening_service._format_session_for_api = MagicMock(return_value=mock_session_data)  # Changed from AsyncMock to MagicMock
        
        result = await awakening_service.create_daily_session(user_id, readiness_level, session_date)
        
        assert result == mock_session_data
        awakening_service.db_session.add.assert_called()
        awakening_service.db_session.flush.assert_called()  # Changed from commit to flush

    @pytest.mark.asyncio
    async def test_complete_quest_success(self, awakening_service):
        """Test successful quest completion"""
        user_id = 1
        quest_id = 1
        progress_data = {'reps': 10, 'time': 60}
        
        # Mock quest and session
        mock_session = MagicMock(spec=AwakeningSession)
        mock_session.user_id = user_id
        mock_session.id = 1
        
        mock_quest = MagicMock(spec=AwakeningQuest)
        mock_quest.id = quest_id
        mock_quest.status = 'active'
        mock_quest.session = mock_session
        mock_quest.session_id = 1
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_quest
        awakening_service.db_session.execute.return_value = mock_result
        
        # Mock validation and reward methods
        awakening_service._validate_quest_completion = MagicMock(return_value=True)  # Changed from AsyncMock to MagicMock
        awakening_service._calculate_quest_rewards = AsyncMock(return_value={'xp': 50, 'aura': 10})
        awakening_service._apply_quest_rewards = AsyncMock()
        awakening_service._check_session_completion = AsyncMock(return_value=False)
        awakening_service.cache_service.invalidate_user_cache = AsyncMock()
        
        result = await awakening_service.complete_quest(user_id, quest_id, progress_data)
        
        assert result['success'] is True
        assert result['quest_id'] == quest_id
        assert 'rewards' in result
        awakening_service.db_session.flush.assert_called_once()  # Changed from commit to flush

    @pytest.mark.asyncio
    async def test_complete_quest_insufficient_progress(self, awakening_service):
        """Test quest completion with insufficient progress"""
        user_id = 1
        quest_id = 1
        progress_data = {'reps': 5, 'time': 30}  # Insufficient
        
        # Mock quest and session
        mock_session = MagicMock(spec=AwakeningSession)
        mock_session.user_id = user_id
        
        mock_quest = MagicMock(spec=AwakeningQuest)
        mock_quest.id = quest_id
        mock_quest.status = 'active'
        mock_quest.session = mock_session
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_quest
        awakening_service.db_session.execute.return_value = mock_result
        
        # Mock validation failure
        awakening_service._validate_quest_completion = MagicMock(return_value=False)  # Changed from AsyncMock to MagicMock
        
        with pytest.raises(ValidationError, match="Progress does not meet quest requirements"):
            await awakening_service.complete_quest(user_id, quest_id, progress_data)
        
        awakening_service.db_session.rollback.assert_called_once()

    @pytest.mark.asyncio
    async def test_reset_daily_session(self, awakening_service):
        """Test resetting a daily session"""
        user_id = 1
        
        # Mock existing session
        mock_session = MagicMock(spec=AwakeningSession)
        mock_session.reset_used = False
        mock_session.tier_level = "hard"
        mock_session.id = 1
        mock_session.quests = []
        
        awakening_service.get_daily_session = AsyncMock(return_value=mock_session)
        
        # Mock quest generation
        mock_quest_data = [
            {
                'quest_type': 'movement_reps',
                'target_movement_id': 2,
                'target_reps': 8,
                'difficulty_level': 'normal'
            }
        ]
        awakening_service.quest_generation_service.generate_daily_quests = AsyncMock(return_value=mock_quest_data)
        
        # Mock cache service and formatting
        awakening_service.cache_service.invalidate_user_cache = AsyncMock()
        mock_session_data = {'session_id': 1, 'tier_level': 'normal'}
        awakening_service._format_session_for_api = MagicMock(return_value=mock_session_data)  # Changed from AsyncMock to MagicMock
        
        result = await awakening_service.reset_daily_session(user_id)

        assert result == mock_session_data
        assert mock_session.reset_used is True
        assert mock_session.tier_level == "normal"  # Reduced from "hard"
        awakening_service.db_session.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_awakening_history(self, awakening_service):
        """Test getting awakening history"""
        user_id = 1
        
        # Mock session data
        mock_session = MagicMock()
        mock_session.id = 1
        mock_session.user_id = user_id
        mock_session.session_date = datetime.now()
        mock_session.status = 'completed'
        mock_session.tier_level = 1
        mock_session.completed_at = datetime.now()
        mock_session.reset_used = False
        mock_session.quests = []
        mock_session.rewards = []
        
        # Mock the database query result
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [mock_session]
        mock_result.scalars.return_value = mock_scalars
        awakening_service.db_session.execute.return_value = mock_result
        
        # Mock greenlet_spawn to return the sessions directly
        with patch('app.application.services.awakening_service.greenlet_spawn') as mock_greenlet:
            mock_greenlet.return_value = [mock_session]
            
            # Mock _format_session_for_api
            awakening_service._format_session_for_api = MagicMock(return_value={'session_id': 1})
            
            result = await awakening_service.get_awakening_history(user_id)
            
            assert len(result) == 1
            assert result[0]['session_id'] == 1
            awakening_service._format_session_for_api.assert_called_once_with(mock_session)

    @pytest.mark.asyncio
    async def test_validate_quest_completion_movement_reps(self, awakening_service):
        """Test quest completion validation for movement reps"""
        # Create mock quest
        mock_quest = MagicMock()
        mock_quest.quest_type = "movement_reps"
        mock_quest.target_reps = 20
        
        # Act & Assert
        assert awakening_service._validate_quest_completion(mock_quest, {"reps": 25}) is True
        assert awakening_service._validate_quest_completion(mock_quest, {"reps": 15}) is False

    @pytest.mark.asyncio
    async def test_validate_quest_completion_time_based(self, awakening_service):
        """Test quest completion validation for time-based quests"""
        # Create mock quest
        mock_quest = MagicMock()
        mock_quest.quest_type = "time_based"
        mock_quest.target_time = 60
        
        # Act & Assert
        assert awakening_service._validate_quest_completion(mock_quest, {"time": 65}) is True
        assert awakening_service._validate_quest_completion(mock_quest, {"time": 45}) is False

    @pytest.mark.asyncio
    async def test_calculate_quest_rewards(self, awakening_service):
        """Test quest reward calculation."""
        # Arrange
        user_id = 1
        mock_quest = MagicMock()
        mock_quest.difficulty_level = "hard"
        mock_quest.session_id = 1
        
        # Mock the _count_completed_quests method to return 3 (meets threshold)
        awakening_service._count_completed_quests = AsyncMock(return_value=3)
        
        # Act
        rewards = await awakening_service._calculate_quest_rewards(mock_quest, user_id)
        
        # Assert
        assert rewards["xp"] == 65  # 50 * 1.3 (hard multiplier)
        assert rewards["aura"] == 13  # 10 * 1.3 (hard multiplier)
        assert rewards["shadow_keys"] == 1  # 3 completed quests meets threshold

    def test_get_quest_count_for_readiness(self, awakening_service):
        """Test quest count determination based on readiness level."""
        assert awakening_service._get_quest_count_for_readiness("low") == 3
        assert awakening_service._get_quest_count_for_readiness("standard") == 3
        assert awakening_service._get_quest_count_for_readiness("high") == 4
        assert awakening_service._get_quest_count_for_readiness("unknown") == 3

    def test_get_difficulty_for_readiness(self, awakening_service):
        """Test difficulty determination based on readiness level."""
        assert awakening_service._get_difficulty_for_readiness("low") == "easy"
        assert awakening_service._get_difficulty_for_readiness("standard") == "moderate"
        assert awakening_service._get_difficulty_for_readiness("high") == "hard"
        assert awakening_service._get_difficulty_for_readiness("unknown") == "moderate"