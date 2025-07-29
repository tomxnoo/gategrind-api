"""
UserSkillProgress SQLAlchemy model for V2 database schema.

This model serves as a join table to track which SkillTreeNodes have been
unlocked by each Ascendant. It represents the progression state of users
through the skill tree system.
"""
from sqlalchemy import Column, Integer, BigInteger, String, ForeignKey, DateTime, Index, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import BaseModel

class UserSkillProgress(BaseModel):
    """
    UserSkillProgress model - Tracks unlocked skill tree nodes for each Ascendant.
    
    This is a critical join table that manages the many-to-many relationship
    between Ascendants and SkillTreeNodes, recording when each node was unlocked.
    
    Fields:
    - ascendant_id: Foreign key to Ascendant who unlocked the node
    - node_id: Foreign key to the SkillTreeNode that was unlocked
    - unlocked_at: Timestamp when the node was unlocked
    """
    __tablename__ = 'user_skill_progress'
    
    # Foreign key relationships
    ascendant_id = Column(BigInteger, ForeignKey('ascendants.id'), nullable=False)
    node_id = Column(String(50), ForeignKey('skill_tree_nodes.node_id'), nullable=False)
    
    # Tracking information
    unlocked_at = Column(DateTime, default=func.now(), nullable=False)
    
    # Relationships
    ascendant = relationship("Ascendant", back_populates="skill_progress")
    node = relationship("SkillTreeNode", back_populates="user_progress")
    
    # Indexes and Constraints for performance and data integrity
    __table_args__ = (
        # Unique constraint to prevent duplicate unlocks
        UniqueConstraint('ascendant_id', 'node_id', name='uq_user_skill_progress_ascendant_node'),
        
        # Performance indexes
        Index('idx_user_skill_progress_ascendant_id', 'ascendant_id'),
        Index('idx_user_skill_progress_node_id', 'node_id'),
        Index('idx_user_skill_progress_unlocked_at', 'unlocked_at'),
        
        # Composite index for common queries (user's progress in specific categories)
        Index('idx_user_skill_progress_ascendant_unlocked', 'ascendant_id', 'unlocked_at'),
    )
    
    def __repr__(self):
        return f"<UserSkillProgress(ascendant_id={self.ascendant_id}, node_id={self.node_id}, unlocked_at='{self.unlocked_at}')>"