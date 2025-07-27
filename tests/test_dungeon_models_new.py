"""
Unit tests for new dungeon system models.
Tests DungeonSession, DungeonTrial, DungeonReward, DailyModifier, and DungeonLevelUnlock models.
"""
import pytest
from datetime import datetime, timezone, date

from app.infrastructure.database.models.v2 import (
    Ascendant, DungeonSession, DungeonTrial, DungeonReward, 
    DailyModifier, DungeonLevelUnlock, DungeonProgress
)


@pytest.fixture
async def sample_ascendant(db_session):
    """Create a sample ascendant for testing"""
    ascendant = Ascendant(
        discord_id="123456789",
        username="TestUser",
        level=10,
        global_xp=5000,
        aura=25,
        skill_points=100,
        strength_points=0,
        endurance_points=0,
        technique_points=0,
        shadow_keys=5
    )
    db_session.add(ascendant)
    await db_session.commit()
    return ascendant


class TestDungeonSession:
    """Test cases for DungeonSession model"""
    
    @pytest.mark.asyncio
    async def test_create_dungeon_session(self, db_session, sample_ascendant):
        """Test creating a basic dungeon session"""
        session = DungeonSession(
            ascendant_id=sample_ascendant.id,
            dungeon_level=3,
            shadow_keys_spent=1
        )
        db_session.add(session)
        await db_session.commit()
        
        assert session.id is not None
        assert session.ascendant_id == sample_ascendant.id
        assert session.dungeon_level == 3
        assert session.status == 'active'
        assert session.shadow_keys_spent == 1
        assert session.is_active is True
        assert session.created_at is not None
    
    @pytest.mark.asyncio
    async def test_session_properties(self, db_session, sample_ascendant):
        """Test session calculated properties"""
        session = DungeonSession(
            ascendant_id=sample_ascendant.id,
            dungeon_level=2,
            shadow_keys_spent=1,
            status='active'
        )
        db_session.add(session)
        await db_session.commit()
        
        # Test basic properties
        assert session.is_active is True
        assert session.is_completed is False
        
        # Complete the session
        session.status = 'completed'
        assert session.is_completed is True


class TestDungeonTrial:
    """Test cases for DungeonTrial model"""
    
    @pytest.mark.asyncio
    async def test_create_dungeon_trial(self, db_session, sample_ascendant):
        """Test creating a basic dungeon trial"""
        # First create a session
        session = DungeonSession(
            ascendant_id=sample_ascendant.id,
            dungeon_level=2,
            shadow_keys_spent=1
        )
        db_session.add(session)
        await db_session.commit()
        
        # Create trial
        trial = DungeonTrial(
            session_id=session.id,
            movement_id=1,
            movement_name='Push-ups',
            target_type='reps',
            target_value=20,
            current_progress=0,
            difficulty_multiplier=1.2
        )
        db_session.add(trial)
        await db_session.commit()
        
        assert trial.id is not None
        assert trial.session_id == session.id
        assert trial.movement_id == 1
        assert trial.movement_name == 'Push-ups'
        assert trial.target_type == 'reps'
        assert trial.target_value == 20
        assert trial.current_progress == 0
        assert trial.difficulty_multiplier == 1.2
        assert trial.is_completed is False
        assert trial.created_at is not None
    
    @pytest.mark.asyncio
    async def test_trial_calculations(self, db_session, sample_ascendant):
        """Test trial progress calculations"""
        # Create session
        session = DungeonSession(
            ascendant_id=sample_ascendant.id,
            dungeon_level=3,
            shadow_keys_spent=1
        )
        db_session.add(session)
        await db_session.commit()
        
        # Create trial with specific values for calculation testing
        trial = DungeonTrial(
            session_id=session.id,
            movement_id=2,
            movement_name='Squats',
            target_type='reps',
            target_value=30,
            current_progress=20,
            difficulty_multiplier=1.5
        )
        db_session.add(trial)
        await db_session.commit()
        
        # Test completion percentage: 20/30 = 66.67%
        assert abs(trial.completion_percentage - 66.66666666666667) < 0.0001
        
        # Test is_successful (should be False - not completed yet)
        assert trial.is_successful is False
        
        # Complete the trial
        trial.current_progress = 30
        trial.is_completed = True
        assert trial.is_successful is True


class TestDungeonReward:
    """Test cases for DungeonReward model"""
    
    @pytest.mark.asyncio
    async def test_create_dungeon_reward(self, db_session, sample_ascendant):
        """Test creating a basic dungeon reward"""
        # Create session first
        session = DungeonSession(
            ascendant_id=sample_ascendant.id,
            dungeon_level=2,
            shadow_keys_spent=1
        )
        db_session.add(session)
        await db_session.commit()
        
        # Create reward
        reward = DungeonReward(
            session_id=session.id,
            ascendant_id=sample_ascendant.id,
            reward_type='aura',
            amount=50
        )
        db_session.add(reward)
        await db_session.commit()
        
        assert reward.id is not None
        assert reward.session_id == session.id
        assert reward.ascendant_id == sample_ascendant.id
        assert reward.reward_type == 'aura'
        assert reward.amount == 50
        assert reward.applied_at is None  # Not applied yet
        assert reward.created_at is not None
    
    @pytest.mark.asyncio
    async def test_reward_types(self, db_session, sample_ascendant):
        """Test different reward types"""
        # Create session
        session = DungeonSession(
            ascendant_id=sample_ascendant.id,
            dungeon_level=3,
            shadow_keys_spent=2
        )
        db_session.add(session)
        await db_session.commit()
        
        # Test aura reward
        aura_reward = DungeonReward(
            session_id=session.id,
            ascendant_id=sample_ascendant.id,
            reward_type='aura',
            amount=100
        )
        db_session.add(aura_reward)
        
        # Test stat_points reward
        stat_reward = DungeonReward(
            session_id=session.id,
            ascendant_id=sample_ascendant.id,
            reward_type='stat_points',
            amount=5
        )
        db_session.add(stat_reward)
        
        # Test shadow_keys reward
        keys_reward = DungeonReward(
            session_id=session.id,
            ascendant_id=sample_ascendant.id,
            reward_type='shadow_keys',
            amount=2
        )
        db_session.add(keys_reward)
        
        await db_session.commit()
        
        assert aura_reward.reward_type == 'aura'
        assert stat_reward.reward_type == 'stat_points'
        assert keys_reward.reward_type == 'shadow_keys'


class TestDailyModifier:
    """Test cases for DailyModifier model"""
    
    @pytest.mark.asyncio
    async def test_create_daily_modifier(self, db_session):
        """Test creating a daily modifier"""
        modifier = DailyModifier(
            modifier_date=date.today(),
            modifier_name='XP Boost Day',
            modifier_type='reward',
            difficulty_multiplier=1.0,
            reward_multiplier=1.5,
            xp_bonus=0.25,
            skill_point_bonus=0.0,
            description='25% XP boost for all dungeon rewards',
            is_active=True
        )
        db_session.add(modifier)
        await db_session.commit()
        
        assert modifier.id is not None
        assert modifier.modifier_date == date.today()
        assert modifier.modifier_name == 'XP Boost Day'
        assert modifier.modifier_type == 'reward'
        assert modifier.difficulty_multiplier == 1.0
        assert modifier.reward_multiplier == 1.5
        assert modifier.xp_bonus == 0.25
        assert modifier.skill_point_bonus == 0.0
        assert modifier.description == '25% XP boost for all dungeon rewards'
        assert modifier.is_active is True
        assert modifier.created_at is not None
    
    @pytest.mark.asyncio
    async def test_modifier_calculations(self, db_session):
        """Test modifier calculation methods"""
        modifier = DailyModifier(
            modifier_date=date.today(),
            modifier_name='Strength Focus',
            modifier_type='mixed',
            difficulty_multiplier=1.2,
            reward_multiplier=1.3,
            xp_bonus=0.15,
            skill_point_bonus=0.20,
            description='Increased difficulty with better rewards',
            is_active=True
        )
        db_session.add(modifier)
        await db_session.commit()
        
        # Test difficulty application
        base_difficulty = 100.0
        modified_difficulty = modifier.apply_to_trial_difficulty(base_difficulty)
        assert modified_difficulty == 120.0  # 100 * 1.2
        
        # Test reward application for XP
        base_xp = 100
        modified_xp = modifier.apply_to_reward(base_xp, 'xp')
        assert modified_xp == 145  # 100 * (1.3 + 0.15) = 145
        
        # Test reward application for skill points
        base_sp = 10
        modified_sp = modifier.apply_to_reward(base_sp, 'skill_points')
        assert modified_sp == 15  # 10 * (1.3 + 0.20) = 15
        
        # Test total reward bonus property
        expected_bonus = max(0.15, 0.20) * 1.3  # max(xp_bonus, skill_point_bonus) * reward_multiplier
        assert modifier.total_reward_bonus == expected_bonus


class TestDungeonLevelUnlock:
    """Test cases for DungeonLevelUnlock model"""
    
    @pytest.mark.asyncio
    async def test_create_dungeon_level_unlock(self, db_session, sample_ascendant):
        """Test creating a dungeon level unlock"""
        # Create DungeonProgress first
        progress = DungeonProgress(
            ascendant_id=sample_ascendant.id,
            highest_level_completed=2,
            total_completions=5,
            total_shadow_keys_spent=5,
            total_shadow_essence_earned=250
        )
        db_session.add(progress)
        await db_session.commit()
        
        # Create unlock requirement
        unlock = DungeonLevelUnlock(
            dungeon_level=3,
            required_ascendant_level=5,
            required_aura=150,
            required_skill_tree_progress=25,
            required_previous_completion=True,
            unlock_description='Complete Level 2 + Aura ≥ 150 + Level 5',
            is_enabled=True
        )
        db_session.add(unlock)
        await db_session.commit()
        
        assert unlock.id is not None
        assert unlock.dungeon_level == 3
        assert unlock.required_ascendant_level == 5
        assert unlock.required_aura == 150
        assert unlock.required_skill_tree_progress == 25
        assert unlock.required_previous_completion is True
        assert unlock.unlock_description == 'Complete Level 2 + Aura ≥ 150 + Level 5'
        assert unlock.is_enabled is True
        assert unlock.created_at is not None
    
    @pytest.mark.asyncio
    async def test_unlock_requirements_check(self, db_session, sample_ascendant):
        """Test unlock requirement checking logic"""
        # Create DungeonProgress
        progress = DungeonProgress(
            ascendant_id=sample_ascendant.id,
            highest_level_completed=1,
            total_completions=2,
            total_shadow_keys_spent=2,
            total_shadow_essence_earned=100
        )
        db_session.add(progress)
        await db_session.commit()
        
        # Create unlock requirement for level 2
        unlock = DungeonLevelUnlock(
            dungeon_level=2,
            required_ascendant_level=3,
            required_aura=75,
            required_skill_tree_progress=10,
            required_previous_completion=True,
            unlock_description='Complete Level 1 + Aura ≥ 75 + Level 3',
            is_enabled=True
        )
        db_session.add(unlock)
        await db_session.commit()
        
        # Test requirement checking (should fail due to ascendant level and aura)
        is_unlocked, missing_reqs = unlock.check_unlock_requirements(sample_ascendant, progress)
        
        # Should not be unlocked due to level and aura requirements
        assert is_unlocked is False
        assert len(missing_reqs) > 0
        
        # Update ascendant to meet requirements
        sample_ascendant.level = 5
        sample_ascendant.aura = 100
        sample_ascendant.skill_points = 15  # Set individual skill points instead of total_skill_points
        
        # Test again - should now be unlocked
        is_unlocked, missing_reqs = unlock.check_unlock_requirements(sample_ascendant, progress)
        assert is_unlocked is True
        assert len(missing_reqs) == 0