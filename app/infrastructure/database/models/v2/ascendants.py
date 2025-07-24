"""
Ascendant SQLAlchemy model for V2 database schema

This model represents the core user data in the GateGrind V2 system.
Each Ascendant has progression stats, skill tree points, and aura calculations.
"""
from sqlalchemy import Column, String, Integer, BigInteger, DateTime, Index
from sqlalchemy.orm import relationship
from .base import BaseModel

class Ascendant(BaseModel):
    """
    Ascendant model - Core user data for GateGrind V2
    
    Fields:
    - discord_id: Unique Discord user identifier
    - username: Current Discord username
    - level: Main Ascendant Level (progression milestone)
    - global_xp: Total XP earned across all activities
    - strength_points: Points available to spend on STR skill tree nodes
    - endurance_points: Points available to spend on END skill tree nodes  
    - technique_points: Points available to spend on TECH skill tree nodes
    - aura: Current aura level (stored value, not calculated)
    - rested_xp_pool: Accumulated rested XP for bonus progression
    - last_login: Timestamp of user's last login for activity tracking
    """
    __tablename__ = "ascendants"
    
    # Core identity fields
    discord_id = Column(String(20), unique=True, nullable=False, index=True)
    username = Column(String(100), nullable=False)
    
    # Progression fields
    level = Column(Integer, default=1, nullable=False)
    global_xp = Column(Integer, default=0, nullable=False)
    aura = Column(Integer, default=0, nullable=False, index=True)
    
    # Skill tree currency - points earned from leveling and milestones
    strength_points = Column(Integer, default=0, nullable=False)
    endurance_points = Column(Integer, default=0, nullable=False)
    technique_points = Column(Integer, default=0, nullable=False)
    
    # Rested XP system for bonus progression
    rested_xp_pool = Column(Integer, default=0, nullable=False)
    
    # User activity tracking
    last_login = Column(DateTime(timezone=True), nullable=True, index=True)
    
    # Relationships
    stats = relationship("AscendantStats", back_populates="ascendant", uselist=False, cascade="all, delete-orphan")
    skill_progress = relationship("UserSkillProgress", back_populates="ascendant", cascade="all, delete-orphan")
    quests = relationship("Quest", back_populates="ascendant", cascade="all, delete-orphan")
    quest_completions = relationship("QuestCompletion", back_populates="ascendant", cascade="all, delete-orphan")
    dungeon_keys = relationship("DungeonKey", back_populates="ascendant", cascade="all, delete-orphan")
    dungeon_progress = relationship("DungeonProgress", back_populates="ascendant", uselist=False, cascade="all, delete-orphan")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_ascendant_discord_id', 'discord_id'),
        Index('idx_ascendant_level', 'level'),
        Index('idx_ascendant_global_xp', 'global_xp'),
        Index('idx_ascendant_aura', 'aura'),
        Index('idx_ascendant_last_login', 'last_login'),
    )
    
    def __repr__(self):
        return f"<Ascendant(discord_id='{self.discord_id}', username='{self.username}', level={self.level})>"
    
    @property
    def total_skill_points(self) -> int:
        """Calculate total skill points available across all trees"""
        return self.strength_points + self.endurance_points + self.technique_points
    
    @property
    def aura_level(self) -> int:
        """
        Calculate current aura level based on progression
        Aura is a composite metric of level, stats, and skill tree progress
        This will be implemented in the ProgressionService
        """
        # Placeholder - actual calculation will be in ProgressionService
        return max(1, self.level // 5)