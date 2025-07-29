"""
Quest and QuestCompletion SQLAlchemy models for V2 database schema.
These models provide a simple, robust log of all quests generated
and completed within the GateGrind ecosystem.
"""
from sqlalchemy import Column, Integer, BigInteger, String, DateTime, ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import BaseModel

class Quest(BaseModel):
    """
    A central log of all quests generated for users. This is a record of a
    quest's existence, not its real-time state.

    Fields:
    - ascendant_id: The user for whom this quest was generated.
    - title: The name of the quest.
    - description: A brief description.
    - source: Where the quest came from ('Awakening', 'Dungeon').
    - status: The final state of the quest ('active', 'completed').
    """
    __tablename__ = 'quests'
    
    ascendant_id = Column(BigInteger, ForeignKey('ascendants.id', ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(String)
    source = Column(String(50), nullable=False, index=True)  # 'Awakening', 'Dungeon_L1', etc.
    status = Column(String(20), default='active', nullable=False, index=True)  # 'active', 'completed', 'expired'
    
    # Relationships
    ascendant = relationship("Ascendant")  # Simple relationship, back_populates not strictly needed on this side
    completion = relationship("QuestCompletion", back_populates="quest", uselist=False, cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_quests_ascendant_status', 'ascendant_id', 'status'),
    )
    
    def __repr__(self):
        return f"<Quest(id={self.id}, ascendant_id={self.ascendant_id}, title='{self.title}')>"

class QuestCompletion(BaseModel):
    """
    A record of a single quest completion event. This acts as an audit log.
    All complex reward calculations are handled by the service layer at the
    time of creation, not stored here.
    """
    __tablename__ = 'quest_completions'
    
    ascendant_id = Column(BigInteger, ForeignKey('ascendants.id', ondelete="CASCADE"), nullable=False)
    quest_id = Column(Integer, ForeignKey('quests.id', ondelete="CASCADE"), nullable=False, unique=True)
    
    # The 'created_at' field from BaseModel serves as the completion timestamp.
    
    # Relationships
    ascendant = relationship("Ascendant", back_populates="quest_completions")
    quest = relationship("Quest", back_populates="completion")
    
    __table_args__ = (
        Index('idx_quest_completions_ascendant_date', 'ascendant_id', 'created_at'),
    )
    
    def __repr__(self):
        return f"<QuestCompletion(quest_id={self.quest_id}, ascendant_id={self.ascendant_id})>"