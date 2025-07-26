"""
Unified profile schema for comprehensive Ascendant profile responses in V2.
This schema combines data from multiple sources and serves as the primary
response model for the /v2/users/me/profile endpoint.
It is a simple data container with no business logic.
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime

# Import the individual schemas we need to compose the profile
from .ascendant_schemas import AscendantBase, AscendantStatsSchema
from .skill_tree_schemas import UserSkillProgressResponse
from .dungeon_schemas import DungeonKeyResponse, DungeonProgressResponse
from .quest_schemas import QuestResponse


class AscendantProfileResponse(AscendantBase):
    """
    Comprehensive profile response that combines all Ascendant-related data.
    The service layer is responsible for assembling this object.
    """
    model_config = ConfigDict(from_attributes=True)
    
    # Core Ascendant Information
    id: int
    discord_id: str
    
    # Detailed Stats Breakdown
    stats: AscendantStatsSchema
    
    # Dungeon System Data
    dungeon_progress: Optional[DungeonProgressResponse] = None
    dungeon_keys: List[DungeonKeyResponse] = []
    
    # Skill Tree Progression
    unlocked_skills: List[UserSkillProgressResponse] = []
    
    # Quest System Data
    active_quests: List[QuestResponse] = []
    
    # Timestamps
    created_at: datetime
    updated_at: datetime