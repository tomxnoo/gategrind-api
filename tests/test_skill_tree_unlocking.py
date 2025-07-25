"""
Tests for skill tree unlocking functionality.

This module tests the complete skill tree unlocking system including:
- Requirement validation (stats, skill points, prerequisites, level)
- Skill point deduction
- UserSkillProgress record creation
- Aura updates
- Error handling and edge cases
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, Mock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.progression_service import ProgressionService, ProgressionResult
from app.infrastructure.database.models.v2 import Ascendant, AscendantStats, UserSkillProgress, SkillTreeNode
from app.application.game_data.skill_tree_config import SkillTreeNode as ConfigNode, SkillNodeRequirements, SkillNodeType


@pytest.fixture
def mock_session():
    """Mock database session."""
    session = AsyncMock(spec=AsyncSession)
    return session


@pytest.fixture
def progression_service(mock_session):
    """Create ProgressionService instance with mocked session."""
    service = ProgressionService(session=mock_session)
    return service


@pytest.fixture
def sample_user():
    """Create a sample user with stats and skill points."""
    user = Ascendant(
        id=1,
        level=5,
        strength_points=10,
        endurance_points=8,
        technique_points=12,
        aura=150
    )
    user.stats = AscendantStats(
        ascendant_id=1,
        str_value=25,
        end_value=20,
        tech_value=30,
        str_level=3,
        end_level=2,
        tech_level=4
    )
    return user


@pytest.fixture
def sample_skill_node():
    """Create a sample skill tree node configuration."""
    requirements = SkillNodeRequirements(
        str_points=20,
        end_points=15,
        tech_points=25,
        strength_skill_points=3,
        endurance_skill_points=2,
        technique_skill_points=4,
        prerequisite_nodes=[],
        min_ascendant_level=3
    )
    
    return ConfigNode(
        id="UPPER_DYNAMIC_L2",
        category_id="UPPER_DYNAMIC",
        level=2,
        name="Advanced Pull-ups",
        description="Master advanced pull-up variations",
        lore_text="The path to upper body mastery continues...",
        node_type=SkillNodeType.PROGRESSION,
        requirements=requirements,
        rewards={"xp_multiplier": 1.2},
        unlock_message="You have unlocked Advanced Pull-ups! Your upper body strength grows."
    )


@pytest.fixture
def sample_db_skill_node():
    """Create a sample database SkillTreeNode record."""
    return SkillTreeNode(
        node_id="UPPER_DYNAMIC_L2",
        category_id="UPPER_DYNAMIC",
        level=2,
        name="Advanced Pull-ups",
        description="Master advanced pull-up variations"
    )


class TestSkillTreeUnlocking:
    """Test cases for skill tree unlocking functionality."""

    @pytest.mark.asyncio
    async def test_unlock_skill_success(self, progression_service, mock_session, sample_user, sample_skill_node, sample_db_skill_node):
        """Test successful skill unlocking."""
        # Mock get_node_by_id to return our sample node
        with patch('app.application.services.progression_service.get_node_by_id', return_value=sample_skill_node):
            # Create mock results for each database query
            mock_results = []
            for return_value in [
                sample_user,  # _get_user_with_skill_progress
                sample_db_skill_node,  # _check_existing_skill_progress (node lookup)
                None,  # _check_existing_skill_progress (no existing progress)
                sample_db_skill_node,  # _create_skill_progress (node lookup)
            ]:
                mock_result = Mock()
                mock_result.scalar_one_or_none.return_value = return_value
                mock_results.append(mock_result)
            
            # Set up the session.execute to return these mock results in sequence
            mock_session.execute.side_effect = mock_results
            
            # Mock transaction execution
            async def mock_transaction(func):
                return await func(mock_session)
            
            progression_service.execute_in_transaction = mock_transaction
            
            # Execute unlock
            result = await progression_service.unlock_skill(user_id=1, node_id="UPPER_DYNAMIC_L2")
            
            # Verify result
            assert result.user_id == 1
            assert result.category == "skill_unlock"
            assert result.node_name == "Advanced Pull-ups"
            assert result.unlock_message == "You have unlocked Advanced Pull-ups! Your upper body strength grows."
            assert result.skill_points_deducted is not None
            assert result.skill_points_deducted['strength_skill_points'] == 3
            assert result.skill_points_deducted['endurance_skill_points'] == 2
            assert result.skill_points_deducted['technique_skill_points'] == 4
            assert result.skill_points_deducted['total'] == 9
            
            # Verify skill points were deducted
            assert sample_user.strength_points == 7  # 10 - 3
            assert sample_user.endurance_points == 6  # 8 - 2
            assert sample_user.technique_points == 8  # 12 - 4

    @pytest.mark.asyncio
    async def test_unlock_skill_node_not_found(self, progression_service):
        """Test unlocking a non-existent skill node."""
        with patch('app.application.services.progression_service.get_node_by_id', return_value=None):
            with pytest.raises(ValueError, match="Skill tree node 'INVALID_NODE' not found"):
                await progression_service.unlock_skill(user_id=1, node_id="INVALID_NODE")

    @pytest.mark.asyncio
    async def test_unlock_skill_user_not_found(self, progression_service, mock_session, sample_skill_node):
        """Test unlocking skill for non-existent user."""
        with patch('app.application.services.progression_service.get_node_by_id', return_value=sample_skill_node):
            mock_result = Mock()
            mock_result.scalar_one_or_none.return_value = None
            mock_session.execute.return_value = mock_result
            
            async def mock_transaction(func):
                return await func(mock_session)
            
            progression_service.execute_in_transaction = mock_transaction
            
            with pytest.raises(Exception, match="User with ID 999 not found"):
                await progression_service.unlock_skill(user_id=999, node_id="UPPER_DYNAMIC_L2")

    @pytest.mark.asyncio
    async def test_unlock_skill_already_unlocked(self, progression_service, mock_session, sample_user, sample_skill_node, sample_db_skill_node):
        """Test unlocking a skill that's already unlocked."""
        with patch('app.application.services.progression_service.get_node_by_id', return_value=sample_skill_node):
            # Mock existing progress
            existing_progress = UserSkillProgress(ascendant_id=1, node_id=1)
            
            # Create mock results for each execute call
            mock_results = [
                Mock(scalar_one_or_none=Mock(return_value=sample_user)),  # _get_user_with_skill_progress
                Mock(scalar_one_or_none=Mock(return_value=sample_db_skill_node)),  # _check_existing_skill_progress (node lookup)
                Mock(scalar_one_or_none=Mock(return_value=existing_progress)),  # _check_existing_skill_progress (existing progress found)
            ]
            mock_session.execute.side_effect = mock_results
            
            async def mock_transaction(func):
                return await func(mock_session)
            
            progression_service.execute_in_transaction = mock_transaction
            
            with pytest.raises(ValueError, match="Skill tree node 'UPPER_DYNAMIC_L2' is already unlocked"):
                await progression_service.unlock_skill(user_id=1, node_id="UPPER_DYNAMIC_L2")

    @pytest.mark.asyncio
    async def test_unlock_skill_insufficient_level(self, progression_service, mock_session, sample_user, sample_skill_node, sample_db_skill_node):
        """Test unlocking skill with insufficient ascendant level."""
        # Set user level below requirement
        sample_user.level = 2
        sample_skill_node.requirements.min_ascendant_level = 5
        
        with patch('app.application.services.progression_service.get_node_by_id', return_value=sample_skill_node):
            mock_results = [
                Mock(scalar_one_or_none=Mock(return_value=sample_user)),  # _get_user_with_skill_progress
                Mock(scalar_one_or_none=Mock(return_value=sample_db_skill_node)),  # _check_existing_skill_progress (node lookup)
                Mock(scalar_one_or_none=Mock(return_value=None)),  # _check_existing_skill_progress (no existing progress)
            ]
            mock_session.execute.side_effect = mock_results
            
            async def mock_transaction(func):
                return await func(mock_session)
            
            progression_service.execute_in_transaction = mock_transaction
            
            with pytest.raises(ValueError, match="Ascendant level 5 required, current level: 2"):
                await progression_service.unlock_skill(user_id=1, node_id="UPPER_DYNAMIC_L2")

    @pytest.mark.asyncio
    async def test_unlock_skill_insufficient_stats(self, progression_service, mock_session, sample_user, sample_skill_node, sample_db_skill_node):
        """Test unlocking skill with insufficient stat values."""
        # Set stat requirements higher than user's stats
        sample_skill_node.requirements.str_points = 50  # User has 25
        
        with patch('app.application.services.progression_service.get_node_by_id', return_value=sample_skill_node):
            mock_results = [
                Mock(scalar_one_or_none=Mock(return_value=sample_user)),  # _get_user_with_skill_progress
                Mock(scalar_one_or_none=Mock(return_value=sample_db_skill_node)),  # _check_existing_skill_progress (node lookup)
                Mock(scalar_one_or_none=Mock(return_value=None)),  # _check_existing_skill_progress (no existing progress)
            ]
            mock_session.execute.side_effect = mock_results
            
            async def mock_transaction(func):
                return await func(mock_session)
            
            progression_service.execute_in_transaction = mock_transaction
            
            with pytest.raises(ValueError, match="Strength stat 50 required, current: 25"):
                await progression_service.unlock_skill(user_id=1, node_id="UPPER_DYNAMIC_L2")

    @pytest.mark.asyncio
    async def test_unlock_skill_insufficient_skill_points(self, progression_service, mock_session, sample_user, sample_skill_node, sample_db_skill_node):
        """Test unlocking skill with insufficient skill points."""
        # Set skill point requirements higher than user's available points
        sample_user.strength_points = 2  # Need 3
        
        with patch('app.application.services.progression_service.get_node_by_id', return_value=sample_skill_node):
            mock_results = [
                Mock(scalar_one_or_none=Mock(return_value=sample_user)),  # _get_user_with_skill_progress
                Mock(scalar_one_or_none=Mock(return_value=sample_db_skill_node)),  # _check_existing_skill_progress (node lookup)
                Mock(scalar_one_or_none=Mock(return_value=None)),  # _check_existing_skill_progress (no existing progress)
            ]
            mock_session.execute.side_effect = mock_results
            
            async def mock_transaction(func):
                return await func(mock_session)
            
            progression_service.execute_in_transaction = mock_transaction
            
            with pytest.raises(ValueError, match="Strength skill points 3 required, available: 2"):
                await progression_service.unlock_skill(user_id=1, node_id="UPPER_DYNAMIC_L2")

    @pytest.mark.asyncio
    async def test_unlock_skill_missing_prerequisites(self, progression_service, mock_session, sample_user, sample_skill_node, sample_db_skill_node):
        """Test unlocking skill with missing prerequisite nodes."""
        # Add prerequisite requirement
        sample_skill_node.requirements.prerequisite_nodes = ["UPPER_DYNAMIC_L1"]
        
        with patch('app.application.services.progression_service.get_node_by_id', return_value=sample_skill_node):
            # Mock prerequisite node lookup
            prereq_node = SkillTreeNode(node_id="UPPER_DYNAMIC_L1", category_id="UPPER_DYNAMIC", level=1, name="Basic Pull-ups")
            
            mock_results = [
                Mock(scalar_one_or_none=Mock(return_value=sample_user)),  # _get_user_with_skill_progress
                Mock(scalar_one_or_none=Mock(return_value=sample_db_skill_node)),  # _check_existing_skill_progress (node lookup)
                Mock(scalar_one_or_none=Mock(return_value=None)),  # _check_existing_skill_progress (no existing progress)
                Mock(scalar_one_or_none=Mock(return_value=prereq_node)),  # _validate_prerequisite_nodes (prereq node lookup)
                Mock(scalar_one_or_none=Mock(return_value=None)),  # _validate_prerequisite_nodes (no prereq progress found)
            ]
            mock_session.execute.side_effect = mock_results
            
            async def mock_transaction(func):
                return await func(mock_session)
            
            progression_service.execute_in_transaction = mock_transaction
            
            with pytest.raises(ValueError, match="Prerequisite skill 'UPPER_DYNAMIC_L1' must be unlocked first"):
                await progression_service.unlock_skill(user_id=1, node_id="UPPER_DYNAMIC_L2")

    @pytest.mark.asyncio
    async def test_unlock_skill_with_prerequisites_met(self, progression_service, mock_session, sample_user, sample_skill_node, sample_db_skill_node):
        """Test unlocking skill with prerequisites properly met."""
        # Add prerequisite requirement
        sample_skill_node.requirements.prerequisite_nodes = ["UPPER_DYNAMIC_L1"]
        
        with patch('app.application.services.progression_service.get_node_by_id', return_value=sample_skill_node):
            # Mock prerequisite node and progress
            prereq_node = SkillTreeNode(node_id="UPPER_DYNAMIC_L1", category_id="UPPER_DYNAMIC", level=1, name="Basic Pull-ups")
            prereq_progress = UserSkillProgress(ascendant_id=1, node_id=1)
            
            mock_results = [
                Mock(scalar_one_or_none=Mock(return_value=sample_user)),  # _get_user_with_skill_progress
                Mock(scalar_one_or_none=Mock(return_value=sample_db_skill_node)),  # _check_existing_skill_progress (node lookup)
                Mock(scalar_one_or_none=Mock(return_value=None)),  # _check_existing_skill_progress (no existing progress)
                Mock(scalar_one_or_none=Mock(return_value=prereq_node)),  # _validate_prerequisite_nodes (prereq node lookup)
                Mock(scalar_one_or_none=Mock(return_value=prereq_progress)),  # _validate_prerequisite_nodes (prereq progress found)
                Mock(scalar_one_or_none=Mock(return_value=sample_db_skill_node)),  # _create_skill_progress (node lookup)
            ]
            mock_session.execute.side_effect = mock_results
            
            async def mock_transaction(func):
                return await func(mock_session)
            
            progression_service.execute_in_transaction = mock_transaction
            
            # Should succeed without raising an exception
            result = await progression_service.unlock_skill(user_id=1, node_id="UPPER_DYNAMIC_L2")
            assert result.node_name == "Advanced Pull-ups"

    @pytest.mark.asyncio
    async def test_unlock_skill_user_without_stats(self, progression_service, mock_session, sample_skill_node, sample_db_skill_node):
        """Test unlocking skill for user without stats record."""
        # Create user without stats
        user_without_stats = Ascendant(
            id=1,
            level=5,
            strength_points=10,
            endurance_points=8,
            technique_points=12,
            aura=150
        )
        user_without_stats.stats = None
        
        # Set requirements that would fail with default stats (10 each)
        sample_skill_node.requirements.str_points = 15
        
        with patch('app.application.services.progression_service.get_node_by_id', return_value=sample_skill_node):
            mock_results = [
                Mock(scalar_one_or_none=Mock(return_value=user_without_stats)),  # _get_user_with_skill_progress
                Mock(scalar_one_or_none=Mock(return_value=sample_db_skill_node)),  # _check_existing_skill_progress (node lookup)
                Mock(scalar_one_or_none=Mock(return_value=None)),  # _check_existing_skill_progress (no existing progress)
            ]
            mock_session.execute.side_effect = mock_results
            
            async def mock_transaction(func):
                return await func(mock_session)
            
            progression_service.execute_in_transaction = mock_transaction
            
            with pytest.raises(ValueError, match="Insufficient stat values to unlock this skill"):
                await progression_service.unlock_skill(user_id=1, node_id="UPPER_DYNAMIC_L2")

    def test_deduct_skill_points(self, progression_service, sample_user, sample_skill_node):
        """Test skill point deduction logic."""
        result = ProgressionResult()
        
        # Store original values
        original_str = sample_user.strength_points
        original_end = sample_user.endurance_points
        original_tech = sample_user.technique_points
        
        # Deduct skill points
        progression_service._deduct_skill_points(sample_user, sample_skill_node, result)
        
        # Verify deductions
        assert sample_user.strength_points == original_str - sample_skill_node.requirements.strength_skill_points
        assert sample_user.endurance_points == original_end - sample_skill_node.requirements.endurance_skill_points
        assert sample_user.technique_points == original_tech - sample_skill_node.requirements.technique_skill_points
        
        # Verify result tracking
        assert result.skill_points_deducted['strength_skill_points'] == sample_skill_node.requirements.strength_skill_points
        assert result.skill_points_deducted['endurance_skill_points'] == sample_skill_node.requirements.endurance_skill_points
        assert result.skill_points_deducted['technique_skill_points'] == sample_skill_node.requirements.technique_skill_points
        assert result.skill_points_deducted['total'] == 9  # 3 + 2 + 4

    @pytest.mark.asyncio
    async def test_create_skill_progress(self, progression_service, mock_session, sample_db_skill_node):
        """Test UserSkillProgress record creation."""
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = sample_db_skill_node
        mock_session.execute.return_value = mock_result
        
        await progression_service._create_skill_progress(mock_session, user_id=1, node_id="UPPER_DYNAMIC_L2")
        
        # Verify session.add was called with UserSkillProgress
        mock_session.add.assert_called_once()
        added_progress = mock_session.add.call_args[0][0]
        assert isinstance(added_progress, UserSkillProgress)
        assert added_progress.ascendant_id == 1
        assert added_progress.node_id == sample_db_skill_node.id

    @pytest.mark.asyncio
    async def test_create_skill_progress_node_not_found(self, progression_service, mock_session):
        """Test UserSkillProgress creation with non-existent node."""
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result
        
        with pytest.raises(ValueError, match="Skill tree node 'INVALID_NODE' not found in database"):
            await progression_service._create_skill_progress(mock_session, user_id=1, node_id="INVALID_NODE")