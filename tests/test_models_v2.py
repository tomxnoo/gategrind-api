"""
Unit tests for V2 database models.
"""
import pytest
from datetime import datetime
from sqlalchemy.exc import IntegrityError

from core.database.models.v2 import (
    Ascendant, AscendantStats, MovementCategory, SkillTreeNode, 
    Movement, UserSkillProgress, Quest, QuestCompletion,
    DungeonKey, DungeonProgress
)


class TestAscendant:
    """Test cases for the Ascendant model."""
    
    def test_create_ascendant(self, db_session, sample_ascendant_data):
        """Test creating a new Ascendant."""
        ascendant = Ascendant(**sample_ascendant_data)
        db_session.add(ascendant)
        db_session.commit()
        
        assert ascendant.id is not None
        assert ascendant.discord_id == sample_ascendant_data["discord_id"]
        assert ascendant.username == sample_ascendant_data["username"]
        assert ascendant.global_xp == sample_ascendant_data["global_xp"]
        assert ascendant.created_at is not None
        assert ascendant.updated_at is not None
    
    def test_ascendant_unique_discord_id(self, db_session, sample_ascendant_data):
        """Test that discord_id must be unique."""
        # Create first ascendant
        ascendant1 = Ascendant(**sample_ascendant_data)
        db_session.add(ascendant1)
        db_session.commit()
        
        # Try to create second ascendant with same discord_id
        sample_ascendant_data["username"] = "different_user"
        ascendant2 = Ascendant(**sample_ascendant_data)
        db_session.add(ascendant2)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_ascendant_last_login_field(self, db_session, sample_ascendant_data):
        """Test that last_login field exists and can be set."""
        ascendant = Ascendant(**sample_ascendant_data)
        ascendant.last_login = datetime.now()
        
        db_session.add(ascendant)
        db_session.commit()
        
        assert ascendant.last_login is not None
        assert isinstance(ascendant.last_login, datetime)


class TestAscendantStats:
    """Test cases for the AscendantStats model."""
    
    def test_create_ascendant_stats(self, db_session, sample_ascendant_data):
        """Test creating AscendantStats with relationship to Ascendant."""
        # Create ascendant first
        ascendant = Ascendant(**sample_ascendant_data)
        db_session.add(ascendant)
        db_session.commit()
        
        # Create stats
        stats = AscendantStats(
            ascendant_id=ascendant.id,
            str_level=2,
            str_xp=50.0,
            end_level=1,
            end_xp=25.0,
            tech_level=3,
            tech_xp=75.0
        )
        db_session.add(stats)
        db_session.commit()
        
        assert stats.id is not None
        assert stats.ascendant_id == ascendant.id
        assert stats.str_level == 2
        assert stats.str_xp == 50.0
    
    def test_ascendant_stats_relationship(self, db_session, sample_ascendant_data):
        """Test the relationship between Ascendant and AscendantStats."""
        ascendant = Ascendant(**sample_ascendant_data)
        db_session.add(ascendant)
        db_session.commit()
        
        stats = AscendantStats(ascendant_id=ascendant.id)
        db_session.add(stats)
        db_session.commit()
        
        # Test relationship access
        assert ascendant.stats == stats
        assert stats.ascendant == ascendant


class TestMovementCategory:
    """Test cases for the MovementCategory model."""
    
    def test_create_movement_category(self, db_session, sample_movement_category_data):
        """Test creating a MovementCategory."""
        category = MovementCategory(**sample_movement_category_data)
        db_session.add(category)
        db_session.commit()
        
        assert category.id is not None
        assert category.name == sample_movement_category_data["name"]
        assert category.primary_stat == sample_movement_category_data["primary_stat"]
        assert category.created_at is not None
        assert category.updated_at is not None
    
    def test_movement_category_unique_name(self, db_session, sample_movement_category_data):
        """Test that category names must be unique."""
        category1 = MovementCategory(**sample_movement_category_data)
        db_session.add(category1)
        db_session.commit()
        
        # Try to create another category with same name
        sample_movement_category_data["primary_stat"] = "different_stat"
        category2 = MovementCategory(**sample_movement_category_data)
        db_session.add(category2)
        
        with pytest.raises(IntegrityError):
            db_session.commit()


class TestSkillTreeNode:
    """Test cases for the SkillTreeNode model."""
    
    def test_create_skill_tree_node(self, db_session, sample_movement_category_data, sample_skill_tree_node_data):
        """Test creating a SkillTreeNode."""
        # Create category first
        category = MovementCategory(**sample_movement_category_data)
        db_session.add(category)
        db_session.commit()
        
        # Create node
        node_data = sample_skill_tree_node_data.copy()
        node_data["category_id"] = category.id
        node = SkillTreeNode(**node_data)
        db_session.add(node)
        db_session.commit()
        
        assert node.id is not None
        assert node.category_id == category.id
        assert node.level == sample_skill_tree_node_data["level"]
        assert node.name == sample_skill_tree_node_data["name"]
        assert node.description == sample_skill_tree_node_data["description"]
        assert node.required_ascendant_level == sample_skill_tree_node_data["required_ascendant_level"]
        assert node.created_at is not None
        assert node.updated_at is not None
    
    def test_skill_tree_node_relationship(self, db_session, sample_movement_category_data, sample_skill_tree_node_data):
        """Test the relationship between MovementCategory and SkillTreeNode."""
        category = MovementCategory(**sample_movement_category_data)
        db_session.add(category)
        db_session.commit()
        
        node_data = sample_skill_tree_node_data.copy()
        node_data["category_id"] = category.id
        node = SkillTreeNode(**node_data)
        db_session.add(node)
        db_session.commit()
        
        # Test relationship access
        assert node.category == category
        assert node in category.skill_tree_nodes


class TestMovement:
    """Test cases for the Movement model."""
    
    def test_create_movement(self, db_session, sample_movement_category_data, sample_skill_tree_node_data, sample_movement_data):
        """Test creating a Movement."""
        # Create category and node first
        category = MovementCategory(**sample_movement_category_data)
        db_session.add(category)
        db_session.commit()
        
        node_data = sample_skill_tree_node_data.copy()
        node_data["category_id"] = category.id
        node = SkillTreeNode(**node_data)
        db_session.add(node)
        db_session.commit()
        
        # Create movement
        movement_data = sample_movement_data.copy()
        movement_data["node_id"] = node.id
        movement = Movement(**movement_data)
        db_session.add(movement)
        db_session.commit()
        
        assert movement.id is not None
        assert movement.node_id == node.id
        assert movement.name == sample_movement_data["name"]
        assert movement.xp_per_rep == sample_movement_data["xp_per_rep"]
        assert movement.stat_reward_type == sample_movement_data["stat_reward_type"]
        assert movement.created_at is not None
        assert movement.updated_at is not None


class TestUserSkillProgress:
    """Test cases for the UserSkillProgress model."""
    
    def test_create_user_skill_progress(self, db_session, sample_ascendant_data, sample_movement_category_data, sample_skill_tree_node_data):
        """Test creating UserSkillProgress."""
        # Create ascendant
        ascendant = Ascendant(**sample_ascendant_data)
        db_session.add(ascendant)
        db_session.commit()
        
        # Create category and node
        category = MovementCategory(**sample_movement_category_data)
        db_session.add(category)
        db_session.commit()
        
        node_data = sample_skill_tree_node_data.copy()
        node_data["category_id"] = category.id
        node = SkillTreeNode(**node_data)
        db_session.add(node)
        db_session.commit()
        
        # Create progress
        progress = UserSkillProgress(
            ascendant_id=ascendant.id,
            node_id=node.id
        )
        db_session.add(progress)
        db_session.commit()
        
        assert progress.id is not None
        assert progress.ascendant_id == ascendant.id
        assert progress.node_id == node.id
        assert progress.unlocked_at is not None
    
    def test_user_skill_progress_unique_constraint(self, db_session, sample_ascendant_data, sample_movement_category_data, sample_skill_tree_node_data):
        """Test that ascendant_id + node_id must be unique."""
        # Create ascendant, category, and node
        ascendant = Ascendant(**sample_ascendant_data)
        db_session.add(ascendant)
        db_session.commit()
        
        category = MovementCategory(**sample_movement_category_data)
        db_session.add(category)
        db_session.commit()
        
        node_data = sample_skill_tree_node_data.copy()
        node_data["category_id"] = category.id
        node = SkillTreeNode(**node_data)
        db_session.add(node)
        db_session.commit()
        
        # Create first progress entry
        progress1 = UserSkillProgress(ascendant_id=ascendant.id, node_id=node.id)
        db_session.add(progress1)
        db_session.commit()
        
        # Try to create duplicate
        progress2 = UserSkillProgress(ascendant_id=ascendant.id, node_id=node.id)
        db_session.add(progress2)
        
        with pytest.raises(IntegrityError):
            db_session.commit()


class TestQuest:
    """Test cases for the Quest model."""
    
    def test_create_quest(self, db_session, sample_ascendant_data):
        """Test creating a Quest."""
        ascendant = Ascendant(**sample_ascendant_data)
        db_session.add(ascendant)
        db_session.commit()
        
        quest = Quest(
            ascendant_id=ascendant.id,
            title="Test Quest",
            description="A test quest",
            source="Awakening",
            status="active"
        )
        db_session.add(quest)
        db_session.commit()
        
        assert quest.id is not None
        assert quest.ascendant_id == ascendant.id
        assert quest.title == "Test Quest"
        assert quest.source == "Awakening"
        assert quest.status == "active"


class TestQuestCompletion:
    """Test cases for the QuestCompletion model."""
    
    def test_create_quest_completion(self, db_session, sample_ascendant_data):
        """Test creating a QuestCompletion."""
        ascendant = Ascendant(**sample_ascendant_data)
        db_session.add(ascendant)
        db_session.commit()
        
        quest = Quest(
            ascendant_id=ascendant.id,
            title="Test Quest",
            source="Awakening"
        )
        db_session.add(quest)
        db_session.commit()
        
        completion = QuestCompletion(
            ascendant_id=ascendant.id,
            quest_id=quest.id
        )
        db_session.add(completion)
        db_session.commit()
        
        assert completion.id is not None
        assert completion.ascendant_id == ascendant.id
        assert completion.quest_id == quest.id
        assert completion.created_at is not None
    
    def test_quest_completion_relationship(self, db_session, sample_ascendant_data):
        """Test the relationship between Quest and QuestCompletion."""
        ascendant = Ascendant(**sample_ascendant_data)
        db_session.add(ascendant)
        db_session.commit()
        
        quest = Quest(
            ascendant_id=ascendant.id,
            title="Test Quest",
            source="Awakening"
        )
        db_session.add(quest)
        db_session.commit()
        
        completion = QuestCompletion(
            ascendant_id=ascendant.id,
            quest_id=quest.id
        )
        db_session.add(completion)
        db_session.commit()
        
        # Test relationship access
        assert quest.completion == completion
        assert completion.quest == quest


class TestDungeonKey:
    """Test cases for the DungeonKey model."""
    
    def test_create_dungeon_key(self, db_session, sample_ascendant_data):
        """Test creating a DungeonKey."""
        ascendant = Ascendant(**sample_ascendant_data)
        db_session.add(ascendant)
        db_session.commit()
        
        key = DungeonKey(
            ascendant_id=ascendant.id,
            key_type="Shadow Key",
            quantity=3
        )
        db_session.add(key)
        db_session.commit()
        
        assert key.id is not None
        assert key.ascendant_id == ascendant.id
        assert key.key_type == "Shadow Key"
        assert key.quantity == 3


class TestDungeonProgress:
    """Test cases for the DungeonProgress model."""
    
    def test_create_dungeon_progress(self, db_session, sample_ascendant_data):
        """Test creating DungeonProgress."""
        ascendant = Ascendant(**sample_ascendant_data)
        db_session.add(ascendant)
        db_session.commit()
        
        progress = DungeonProgress(
            ascendant_id=ascendant.id,
            highest_level_completed=5
        )
        db_session.add(progress)
        db_session.commit()
        
        assert progress.id is not None
        assert progress.ascendant_id == ascendant.id
        assert progress.highest_level_completed == 5