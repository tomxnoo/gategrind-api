"""
DungeonLevelUnlock SQLAlchemy model for V2 database schema.
This model manages unlock requirements for different dungeon levels.
"""
from sqlalchemy import Column, Integer, String, Boolean, Text, Index
from sqlalchemy.orm import relationship

from .base import BaseModel


class DungeonLevelUnlock(BaseModel):
    """
    DungeonLevelUnlock model - Manages unlock requirements for dungeon levels.
    
    Fields:
    - dungeon_level: The dungeon level unlocked (infinite progression)
    - required_ascendant_level: Minimum ascendant level required
    - required_aura: Minimum aura level required
    - required_skill_tree_progress: Required skill tree completion percentage
    - required_previous_completion: Whether previous level must be completed
    - unlock_description: Human-readable description of requirements
    - is_enabled: Whether this level is currently enabled
    - unlock_data: JSON data for additional unlock requirements
    """
    __tablename__ = 'dungeon_level_unlocks'
    
    dungeon_level = Column(Integer, nullable=False, unique=True, index=True)  # Infinite progression supported
    required_ascendant_level = Column(Integer, nullable=False, default=1)
    required_aura = Column(Integer, nullable=False, default=0)
    required_skill_tree_progress = Column(Integer, nullable=False, default=0)  # Percentage 0-100
    required_previous_completion = Column(Boolean, nullable=False, default=True)
    unlock_description = Column(Text, nullable=False)
    is_enabled = Column(Boolean, nullable=False, default=True)
    unlock_data = Column(Text, nullable=True)  # JSON storage for additional requirements
    
    __table_args__ = (
        Index('idx_dungeon_unlocks_level', 'dungeon_level'),
        Index('idx_dungeon_unlocks_enabled', 'is_enabled'),
        Index('idx_dungeon_unlocks_aura', 'required_aura'),
        Index('idx_dungeon_unlocks_ascendant_level', 'required_ascendant_level'),
    )
    
    def __repr__(self):
        return f"<DungeonLevelUnlock(level={self.dungeon_level}, req_level={self.required_ascendant_level}, req_aura={self.required_aura})>"
    
    def check_unlock_requirements(self, ascendant, dungeon_progress=None) -> tuple[bool, list[str]]:
        """
        Check if an ascendant meets the unlock requirements for this dungeon level.
        
        Returns:
            tuple: (is_unlocked, list_of_missing_requirements)
        """
        missing_requirements = []
        
        # Check ascendant level requirement
        if ascendant.level < self.required_ascendant_level:
            missing_requirements.append(f"Ascendant Level {self.required_ascendant_level} required (current: {ascendant.level})")
        
        # Check aura requirement
        if ascendant.aura < self.required_aura:
            missing_requirements.append(f"Aura Level {self.required_aura} required (current: {ascendant.aura})")
        
        # Check skill tree progress requirement
        if self.required_skill_tree_progress > 0:
            # This would need to be calculated based on actual skill tree progress
            # For now, we'll assume it's met if they have any skill points spent
            total_skill_points_spent = ascendant.total_skill_points
            if total_skill_points_spent < self.required_skill_tree_progress:
                missing_requirements.append(f"Skill Tree Progress {self.required_skill_tree_progress}% required")
        
        # Check previous level completion requirement
        if self.required_previous_completion and self.dungeon_level > 1:
            if not dungeon_progress or dungeon_progress.highest_level_completed < (self.dungeon_level - 1):
                missing_requirements.append(f"Must complete Dungeon Level {self.dungeon_level - 1} first")
        
        # Check if level is enabled
        if not self.is_enabled:
            missing_requirements.append("This dungeon level is currently disabled")
        
        return len(missing_requirements) == 0, missing_requirements
    
    @classmethod
    def get_unlocked_levels(cls, session, ascendant, dungeon_progress=None) -> list[int]:
        """Get all dungeon levels that are unlocked for an ascendant"""
        unlocked_levels = []
        
        # Get all unlock requirements ordered by level
        unlock_requirements = session.query(cls).filter(cls.is_enabled == True).order_by(cls.dungeon_level).all()
        
        for unlock_req in unlock_requirements:
            is_unlocked, _ = unlock_req.check_unlock_requirements(ascendant, dungeon_progress)
            if is_unlocked:
                unlocked_levels.append(unlock_req.dungeon_level)
        
        return unlocked_levels
    
    @classmethod
    def get_max_unlocked_level(cls, session, ascendant, dungeon_progress=None) -> int:
        """Get the highest dungeon level unlocked for an ascendant"""
        unlocked_levels = cls.get_unlocked_levels(session, ascendant, dungeon_progress)
        return max(unlocked_levels) if unlocked_levels else 0