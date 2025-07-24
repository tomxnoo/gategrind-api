"""
DungeonProgress SQLAlchemy model for V2 database schema.
This model tracks the highest dungeon level completed by each user.
"""
from sqlalchemy import Column, Integer, ForeignKey, Index
from sqlalchemy.orm import relationship

from .base import BaseModel


class DungeonProgress(BaseModel):
    """
    DungeonProgress model - Tracks the highest dungeon level completed by each user.
    
    Fields:
    - ascendant_id: The user whose progress is being tracked.
    - highest_level_completed: The highest dungeon level this user has successfully completed.
    """
    __tablename__ = 'dungeon_progress'
    
    ascendant_id = Column(Integer, ForeignKey('ascendants.id', ondelete="CASCADE"), nullable=False, unique=True)
    highest_level_completed = Column(Integer, nullable=False, default=0)
    
    # Relationships
    ascendant = relationship("Ascendant", back_populates="dungeon_progress", uselist=False)
    
    __table_args__ = (
        Index('idx_dungeon_progress_ascendant', 'ascendant_id'),
        Index('idx_dungeon_progress_level', 'highest_level_completed'),
    )
    
    def __repr__(self):
        return f"<DungeonProgress(ascendant_id={self.ascendant_id}, highest_level_completed={self.highest_level_completed})>"