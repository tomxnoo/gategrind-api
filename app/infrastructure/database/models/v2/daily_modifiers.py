"""
DailyModifier SQLAlchemy model for V2 database schema.
This model manages daily dungeon modifiers that affect difficulty and rewards.
"""
from sqlalchemy import Column, Integer, String, Date, Float, Boolean, Text, Index
from sqlalchemy.orm import relationship
from datetime import date

from .base import BaseModel


class DailyModifier(BaseModel):
    """
    DailyModifier model - Manages daily dungeon modifiers for difficulty and rewards.
    
    Fields:
    - modifier_date: The date this modifier is active for
    - modifier_name: Display name of the modifier
    - modifier_type: Type of modifier effect
    - difficulty_multiplier: Multiplier applied to trial difficulty
    - reward_multiplier: Multiplier applied to rewards
    - xp_bonus: Flat XP bonus percentage
    - skill_point_bonus: Flat skill point bonus percentage
    - description: Human-readable description of the modifier
    - is_active: Whether this modifier is currently active
    - modifier_data: JSON data for modifier-specific configuration
    """
    __tablename__ = 'daily_modifiers'
    
    modifier_date = Column(Date, nullable=False, unique=True, index=True)
    modifier_name = Column(String(100), nullable=False)
    modifier_type = Column(String(30), nullable=False)  # 'difficulty', 'reward', 'mixed', 'special'
    difficulty_multiplier = Column(Float, nullable=False, default=1.0)
    reward_multiplier = Column(Float, nullable=False, default=1.0)
    xp_bonus = Column(Float, nullable=False, default=0.0)  # Percentage bonus (0.25 = 25%)
    skill_point_bonus = Column(Float, nullable=False, default=0.0)  # Percentage bonus
    description = Column(Text, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    modifier_data = Column(Text, nullable=True)  # JSON storage for modifier-specific data
    
    __table_args__ = (
        Index('idx_daily_modifiers_date', 'modifier_date'),
        Index('idx_daily_modifiers_type', 'modifier_type'),
        Index('idx_daily_modifiers_active', 'is_active'),
    )
    
    def __repr__(self):
        return f"<DailyModifier(date={self.modifier_date}, name='{self.modifier_name}', type='{self.modifier_type}')>"
    
    @property
    def is_today(self) -> bool:
        """Check if this modifier is for today"""
        return self.modifier_date == date.today()
    
    @property
    def total_reward_bonus(self) -> float:
        """Calculate total reward bonus including XP and skill points"""
        return max(self.xp_bonus, self.skill_point_bonus) * self.reward_multiplier
    
    @classmethod
    def get_today_modifier(cls, session):
        """Get today's active modifier"""
        return session.query(cls).filter(
            cls.modifier_date == date.today(),
            cls.is_active == True
        ).first()
    
    def apply_to_trial_difficulty(self, base_difficulty: float) -> float:
        """Apply modifier to trial difficulty"""
        return base_difficulty * self.difficulty_multiplier
    
    def apply_to_reward(self, base_reward: int, reward_type: str) -> int:
        """Apply modifier to reward amount"""
        multiplier = self.reward_multiplier
        
        if reward_type == 'xp':
            multiplier += self.xp_bonus
        elif reward_type == 'skill_points':
            multiplier += self.skill_point_bonus
        
        return int(base_reward * multiplier)