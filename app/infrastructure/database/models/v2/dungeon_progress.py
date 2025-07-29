"""
DungeonProgress SQLAlchemy model for V2 database schema.
This model tracks the highest dungeon level completed by each user.
"""
from sqlalchemy import Column, Integer, BigInteger, ForeignKey, Index, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from .base import BaseModel


class DungeonProgress(BaseModel):
    """
    DungeonProgress model - Tracks the highest dungeon level completed by each user.
    
    Fields:
    - ascendant_id: The user whose progress is being tracked.
    - highest_level_completed: The highest dungeon level this user has successfully completed.
    - total_completions: Total number of dungeon completions across all levels
    - total_shadow_keys_spent: Total shadow keys spent on dungeon entries
    - total_shadow_essence_earned: Total shadow essence earned from completions
    - last_completion_date: Date of the most recent dungeon completion
    - best_completion_time: Best completion time in seconds across all dungeons
    """
    __tablename__ = 'dungeon_progress'
    
    ascendant_id = Column(BigInteger, ForeignKey('ascendants.id', ondelete="CASCADE"), nullable=False, unique=True)
    highest_level_completed = Column(Integer, nullable=False, default=0)
    total_completions = Column(Integer, nullable=False, default=0)
    total_shadow_keys_spent = Column(Integer, nullable=False, default=0)
    total_shadow_essence_earned = Column(Integer, nullable=False, default=0)
    last_completion_date = Column(DateTime(timezone=True), nullable=True)
    best_completion_time = Column(Integer, nullable=True)  # in seconds
    
    # Relationships
    ascendant = relationship("Ascendant", back_populates="dungeon_progress", uselist=False)
    
    __table_args__ = (
        Index('idx_dungeon_progress_ascendant', 'ascendant_id'),
        Index('idx_dungeon_progress_level', 'highest_level_completed'),
        Index('idx_dungeon_progress_completions', 'total_completions'),
        Index('idx_dungeon_progress_last_completion', 'last_completion_date'),
    )
    
    def __repr__(self):
        return f"<DungeonProgress(ascendant_id={self.ascendant_id}, highest_level_completed={self.highest_level_completed}, total_completions={self.total_completions})>"