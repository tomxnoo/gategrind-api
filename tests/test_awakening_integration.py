"""Integration tests for awakening system."""
import pytest
from datetime import date, datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.infrastructure.database.models.v2.ascendants import Ascendant
from app.infrastructure.database.models.v2.awakening import AwakeningSession
from app.infrastructure.database.models.v2.movements import Movement
from app.infrastructure.database.models.v2.movement_categories import MovementCategory
from app.infrastructure.database.models.v2.skill_tree_nodes import SkillTreeNode
from app.infrastructure.database.models.v2.user_skill_progress import UserSkillProgress
from app.application.services.awakening_service import AwakeningService
from app.application.services.progression_service import ProgressionService


@pytest.fixture
async def test_user(db_session: AsyncSession):
    """Create a test user and eagerly load necessary relationships."""
    user = Ascendant(
        discord_id="123456789012345678",
        username="testuser",
        level=5,
        global_xp=1000,
        aura=100,
        awakening_streak=0
    )
    db_session.add(user)
    await db_session.commit()

    query = (
        select(Ascendant)
        .options(selectinload(Ascendant.awakening_sessions))
        .filter(Ascendant.id == user.id)
    )
    result = await db_session.execute(query)
    return result.scalar_one()


@pytest.fixture
async def test_user_with_skills(db_session: AsyncSession, test_user, test_movements):
    """Add skill progress to the test user so they have access to movements."""
    # Get the skill node that movements are associated with
    node_query = select(SkillTreeNode).where(SkillTreeNode.node_id == "BODYWEIGHT_1")
    node_result = await db_session.execute(node_query)
    skill_node = node_result.scalar_one()
    
    # Create UserSkillProgress entry to unlock the skill node - use the node's primary key
    skill_progress = UserSkillProgress(
        ascendant_id=test_user.id,
        node_id=skill_node.id,  # This should be the integer primary key
        unlocked_at=datetime.utcnow()
    )
    db_session.add(skill_progress)
    await db_session.commit()
    
    return test_user


@pytest.fixture
async def test_movements(db_session: AsyncSession):
    """Create test movements and categories with eager loading."""
    category = MovementCategory(
        id="BODYWEIGHT", name="Bodyweight", primary_stat="STR"
    )
    db_session.add(category)
    await db_session.commit()

    node = SkillTreeNode(
        node_id="BODYWEIGHT_1",
        category_id="BODYWEIGHT",
        level=1,
        name="Foundation",
        description="Basic bodyweight movements",
        required_ascendant_level=1,
        required_str_points=0,
        required_end_points=0,
        required_tech_points=0,
    )
    db_session.add(node)
    await db_session.commit()

    movement_names = ["Push-ups", "Squats", "Burpees"]
    movements_to_create = [
        Movement(
            node_id=node.id,
            name=name,
            xp_per_rep=1.5 if name == "Push-ups" else (1.0 if name == "Squats" else 2.0),
            stat_reward_type="STR" if name == "Push-ups" else "END",
        )
        for name in movement_names
    ]
    db_session.add_all(movements_to_create)
    await db_session.commit()

    query = (
        select(Movement)
        .options(selectinload(Movement.node))
        .where(Movement.name.in_(movement_names))
    )
    result = await db_session.execute(query)
    return result.scalars().all()


@pytest.fixture
async def awakening_service(db_session: AsyncSession):
    """Create awakening service with test session."""
    progression_service = ProgressionService(db_session)
    return AwakeningService(db_session, progression_service)


class TestAwakeningIntegration:
    """Integration tests for the awakening system."""

    @pytest.mark.asyncio
    async def test_debug_quest_generation(self, test_user_with_skills, test_movements, db_session: AsyncSession):
        """Debug test to check quest generation directly."""
        from app.application.services.quest_generation_service import QuestGenerationService
        from datetime import date
        
        user_id = test_user_with_skills.id
        today = date.today()
        
        # Create quest generation service
        quest_service = QuestGenerationService(db_session)
        
        try:
            # Try to generate quests directly
            print(f"\n=== QUEST GENERATION DEBUG ===")
            print(f"User ID: {user_id}")
            print(f"Date: {today}")
            
            quests = await quest_service.generate_daily_quests(
                user_id=user_id,
                session_date=today,
                tier_level="normal",
                readiness_level_override=5
            )
            
            print(f"Generated {len(quests)} quests")
            for quest in quests:
                print(f"  Quest: {quest}")
            print("=" * 30)
            
            assert len(quests) > 0
            
        except Exception as e:
            print(f"Error: {e}")
            print("=" * 30)
            raise

    @pytest.mark.asyncio
    async def test_full_awakening_workflow(self, test_user_with_skills, test_movements, awakening_service, db_session: AsyncSession):
        """Test the complete awakening workflow from session creation to completion."""
        user_id = test_user_with_skills.id
        today = date.today()

        # Step 1: Create daily session
        session_data = await awakening_service.create_daily_session(user_id, 5, today, "normal")

        assert session_data is not None
        assert "session_id" in session_data
        assert "quests" in session_data
        assert len(session_data["quests"]) >= 3

        quests = session_data["quests"]

        # Step 2: Complete each quest
        for i, quest in enumerate(quests):
            progress_data = {}
            if quest["quest_type"] == "movement_reps":
                progress_data = {"reps": quest["target_reps"] + 5}
            elif quest["quest_type"] == "time_based":
                target_time = quest.get("target_time", 60)
                progress_data = {"time": target_time + 10}
            elif quest["quest_type"] == "endurance_challenge":
                # For endurance challenge, provide both reps and time that exceed targets
                progress_data = {
                    "reps": quest["target_reps"] + 5,
                    "time": quest["target_time"] + 10
                }

            # Debug: Print quest details before completion
            print(f"\n=== QUEST COMPLETION DEBUG (Quest {i+1}) ===")
            print(f"Quest ID: {quest['id']}")
            print(f"Quest Type: {quest.get('quest_type')}")
            print(f"Target Reps: {quest.get('target_reps')}")
            print(f"Target Time: {quest.get('target_time')}")
            print(f"Target Distance: {quest.get('target_distance')}")
            print(f"Progress Data: {progress_data}")
            print(f"Full Quest Data: {quest}")
            print("=" * 40)

            result = await awakening_service.complete_quest(user_id, quest["id"], progress_data)

            assert result["success"] is True
            assert result["quest_id"] == quest["id"]
            if i == len(quests) - 1:
                assert result["session_complete"] is True
            else:
                assert result["session_complete"] is False

        # Step 3: Verify session completion
        final_session = await awakening_service.get_daily_session(user_id, today)
        assert final_session.status == "completed"

        # Step 4: Verify user's awakening streak was updated
        result = await db_session.execute(select(Ascendant).where(Ascendant.id == user_id))
        updated_user = result.scalar_one()
        assert updated_user.awakening_streak == 1

    @pytest.mark.asyncio
    async def test_daily_session_uniqueness(self, test_user_with_skills, test_movements, awakening_service):
        """Test that only one session per day can be created."""
        user_id = test_user_with_skills.id
        today = date.today()

        session1 = await awakening_service.create_daily_session(user_id, 5, today, "normal")
        assert session1 is not None

        session2 = await awakening_service.get_daily_session(user_id, today)
        assert session2 is not None
        assert session2.id == session1["session_id"]

    @pytest.mark.asyncio
    async def test_quest_validation_failure(self, test_user_with_skills, test_movements, awakening_service):
        """Test quest completion with insufficient progress."""
        from app.application.services.awakening_service import ValidationError
        
        user_id = test_user_with_skills.id
        today = date.today()

        session_data = await awakening_service.create_daily_session(user_id, 5, today, "normal")
        quest = session_data["quests"][0]

        progress_data = {}
        if quest["quest_type"] == "movement_reps":
            progress_data = {"reps": quest["target_reps"] - 5}
        elif quest["quest_type"] == "time_based":
            progress_data = {"time": quest.get("target_time", 60) - 10}
        elif quest["quest_type"] == "endurance_challenge":
            # For endurance challenge, provide insufficient progress
            progress_data = {
                "reps": quest["target_reps"] - 5,
                "time": quest["target_time"] - 10
            }

        # Should raise ValidationError
        with pytest.raises(ValidationError) as exc_info:
            await awakening_service.complete_quest(user_id, quest["id"], progress_data)
        
        # Check that the error message indicates validation failure
        assert "does not meet" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_session_reset(self, test_user_with_skills, test_movements, awakening_service):
        """Test resetting an awakening session."""
        user_id = test_user_with_skills.id
        today = date.today()

        session_data = await awakening_service.create_daily_session(user_id, 5, today, "normal")

        quest = session_data["quests"][0]
        progress_data = {}
        if quest["quest_type"] == "movement_reps":
            progress_data = {"reps": quest["target_reps"] + 5}
        elif quest["quest_type"] == "time_based":
            progress_data = {"time": quest.get("target_time", 60) + 10}
        elif quest["quest_type"] == "endurance_challenge":
            progress_data = {
                "reps": quest["target_reps"] + 5,
                "time": quest["target_time"] + 10
            }
        await awakening_service.complete_quest(user_id, quest["id"], progress_data)

        reset_result = await awakening_service.reset_daily_session(user_id)
        assert reset_result["session_id"] is not None
        assert reset_result["reset_used"] is True

        session_after_reset = await awakening_service.get_daily_session(user_id, today)
        assert session_after_reset is not None
        assert session_after_reset.reset_used is True

    @pytest.mark.asyncio
    async def test_awakening_history(self, test_user_with_skills, test_movements, awakening_service):
        """Test awakening history retrieval."""
        user_id = test_user_with_skills.id
        today = date.today()

        session_data = await awakening_service.create_daily_session(user_id, 8, today, "normal")

        for quest in session_data["quests"]:
            progress_data = {}
            if quest["quest_type"] == "movement_reps":
                progress_data = {"reps": quest["target_reps"] + 5}
            elif quest["quest_type"] == "time_based":
                progress_data = {"time": quest.get("target_time", 60) + 10}
            elif quest["quest_type"] == "endurance_challenge":
                progress_data = {
                    "reps": quest["target_reps"] + 5,
                    "time": quest["target_time"] + 10
                }
            await awakening_service.complete_quest(user_id, quest["id"], progress_data)

        history = await awakening_service.get_awakening_history(user_id, limit=10)

        assert len(history) == 1
        assert history[0]["session_id"] == session_data["session_id"]
        assert history[0]["status"] == "completed"
        assert len(history[0]["quests"]) >= 3
        assert len(history[0]["rewards"]) > 0

    @pytest.mark.asyncio
    async def test_different_readiness_levels(self, test_user_with_skills, test_movements, awakening_service):
        """Test session creation with different readiness levels."""
        user_id = test_user_with_skills.id
        today = date.today()

        low_session = await awakening_service.create_daily_session(user_id, 2, today, "normal")
        assert len(low_session["quests"]) >= 3
        await awakening_service.reset_daily_session(user_id)

        standard_session = await awakening_service.create_daily_session(user_id, 5, today, "normal")
        assert len(standard_session["quests"]) >= 3
        await awakening_service.reset_daily_session(user_id)

        high_session = await awakening_service.create_daily_session(user_id, 8, today, "normal")
        assert len(high_session["quests"]) >= 4

    @pytest.mark.asyncio
    async def test_streak_calculation(self, test_user_with_skills, test_movements, awakening_service, db_session: AsyncSession):
        """Test streak calculation logic."""
        user_id = test_user_with_skills.id
        today = date.today()

        # Complete today's session
        session_data = await awakening_service.create_daily_session(user_id, 5, today, "normal")
        for quest in session_data["quests"]:
            progress_data = {}
            if quest["quest_type"] == "movement_reps":
                progress_data = {"reps": quest["target_reps"] + 5}
            elif quest["quest_type"] == "time_based":
                progress_data = {"time": quest.get("target_time", 60) + 10}
            elif quest["quest_type"] == "endurance_challenge":
                progress_data = {
                    "reps": quest["target_reps"] + 5,
                    "time": quest["target_time"] + 10
                }
            await awakening_service.complete_quest(user_id, quest["id"], progress_data)

        # Check that streak is 1 after first completion
        result = await db_session.execute(select(Ascendant).where(Ascendant.id == user_id))
        updated_user = result.scalar_one()
        assert updated_user.awakening_streak == 1

        # Add a completed session for yesterday to simulate consecutive days
        yesterday = date.today() - timedelta(days=1)
        yesterday_session = AwakeningSession(
            user_id=user_id,
            session_date=yesterday,
            status="completed",
            completed_at=datetime.utcnow(),
        )
        db_session.add(yesterday_session)
        await db_session.commit()

        # Now simulate completing a session for tomorrow (next day)
        tomorrow = date.today() + timedelta(days=1)
        tomorrow_session_data = await awakening_service.create_daily_session(user_id, 5, tomorrow, "normal")
        for quest in tomorrow_session_data["quests"]:
            progress_data = {}
            if quest["quest_type"] == "movement_reps":
                progress_data = {"reps": quest["target_reps"] + 5}
            elif quest["quest_type"] == "time_based":
                progress_data = {"time": quest.get("target_time", 60) + 10}
            elif quest["quest_type"] == "endurance_challenge":
                progress_data = {
                    "reps": quest["target_reps"] + 5,
                    "time": quest["target_time"] + 10
                }
            await awakening_service.complete_quest(user_id, quest["id"], progress_data)

        # Check that streak is now 2 after consecutive day completion
        result = await db_session.execute(select(Ascendant).where(Ascendant.id == user_id))
        updated_user = result.scalar_one()
        assert updated_user.awakening_streak == 2

    @pytest.mark.asyncio
    async def test_api_integration(self, test_user_with_skills, test_movements, awakening_service):
        """Test full API integration flow."""
        user_id = test_user_with_skills.id
        today = date.today()

        session_data = await awakening_service.create_daily_session(user_id, 6, today, "normal")

        assert "session_id" in session_data
        assert "quests" in session_data
        assert "status" in session_data
        assert session_data["status"] == "active"

        quest = session_data["quests"][0]
        
        progress_data = {}
        if quest["quest_type"] == "movement_reps":
            progress_data = {"reps": quest["target_reps"] + 5}  # More than target amount
        elif quest["quest_type"] == "time_based":
            progress_data = {"time": quest.get("target_time", 60) + 10}  # More than target amount
        elif quest["quest_type"] == "endurance_challenge":
            progress_data = {
                "reps": quest["target_reps"] + 5,
                "time": quest["target_time"] + 10
            }
            
        result = await awakening_service.complete_quest(user_id, quest["id"], progress_data)

        assert result["success"] is True
        assert result["quest_id"] == quest["id"]
        assert "rewards" in result
        assert "xp" in result["rewards"]

        # Get the updated session object and check its ID
        updated_session = await awakening_service.get_daily_session(user_id, today)
        assert updated_session is not None
        assert updated_session.id == session_data["session_id"]

    @pytest.mark.asyncio
    async def test_reward_calculation_and_application(self, test_user_with_skills, test_movements, awakening_service, db_session: AsyncSession):
        """Test that rewards are correctly calculated and applied."""
        user_id = test_user_with_skills.id
        today = date.today()
        initial_xp = test_user_with_skills.global_xp
        initial_aura = test_user_with_skills.aura

        session_data = await awakening_service.create_daily_session(user_id, 8, today, "high")

        total_expected_xp = 0
        total_expected_aura = 0

        for quest in session_data["quests"]:
            progress_data = {}
            if quest["quest_type"] == "movement_reps":
                progress_data = {"reps": quest["target_reps"] + 5}
            elif quest["quest_type"] == "time_based":
                progress_data = {"time": quest.get("target_time", 60) + 10}
            elif quest["quest_type"] == "endurance_challenge":
                progress_data = {
                    "reps": quest["target_reps"] + 5,
                    "time": quest["target_time"] + 10
                }
            result = await awakening_service.complete_quest(user_id, quest["id"], progress_data)

            total_expected_xp += result["rewards"]["xp"]
            total_expected_aura += result["rewards"]["aura"]

        result = await db_session.execute(select(Ascendant).where(Ascendant.id == user_id))
        updated_user = result.scalar_one()

        assert updated_user.global_xp >= initial_xp + total_expected_xp
        assert updated_user.aura >= initial_aura + total_expected_aura

    @pytest.mark.asyncio
    async def test_new_day_creates_new_session(self, test_user_with_skills, test_movements, awakening_service):
        """Test that a new session is created on a new day."""
        user_id = test_user_with_skills.id
        today = date.today()
        
        # Create a session for today
        session_data = await awakening_service.create_daily_session(user_id, 5, today, "normal")
        
        # Complete the first quest
        quest_id = session_data["quests"][0]["id"]
        progress_data = {"reps": 15}  # Should meet the requirement
        
        # Debug: Print quest details before completion
        quest_details = session_data["quests"][0]
        print(f"\n=== QUEST COMPLETION DEBUG ===")
        print(f"Quest ID: {quest_id}")
        print(f"Quest Type: {quest_details.get('quest_type')}")
        print(f"Target Reps: {quest_details.get('target_reps')}")
        print(f"Target Time: {quest_details.get('target_time')}")
        print(f"Target Distance: {quest_details.get('target_distance')}")
        print(f"Progress Data: {progress_data}")
        print(f"Quest Details: {quest_details}")
        print("=" * 30)
        
        completion_result = await awakening_service.complete_quest(
            user_id=user_id,
            quest_id=quest_id,
            progress_data=progress_data
        )
        
        assert completion_result["success"] is True