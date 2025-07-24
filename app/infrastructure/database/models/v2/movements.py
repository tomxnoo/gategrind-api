"""
Movement SQLAlchemy model for V2 database schema.

This model represents individual exercises that belong to specific
skill tree nodes. Each movement has its own XP and stat reward configuration.
"""
from sqlalchemy import Column, String, Integer, Float, ForeignKey, Index, CheckConstraint, Enum
from sqlalchemy.orm import relationship

from .base import BaseModel

class Movement(BaseModel):
    """
    Movement model - Individual exercises linked to skill tree nodes.
    
    Fields:
    - node_id: Foreign key to SkillTreeNode.
    - name: The exercise name (e.g., "Negative Pull-ups").
    - xp_per_rep: Global XP awarded per repetition.
    - stat_reward_type: The core stat (STR, END, TECH) that this movement rewards.
    """
    __tablename__ = 'movements'
    
    # Core identification and linking
    node_id = Column(Integer, ForeignKey('skill_tree_nodes.id'), nullable=False)
    name = Column(String(100), nullable=False)
    xp_per_rep = Column(Float, default=1.0, nullable=False)
    stat_reward_type = Column(Enum('STR', 'END', 'TECH', name='stat_enum'), nullable=False)
    
    # Relationships
    node = relationship("SkillTreeNode", back_populates="movements")
    
    # Indexes and Constraints for performance and data integrity
    __table_args__ = (
        Index('idx_movements_node_id', 'node_id'),
        Index('idx_movements_name', 'name'),
        CheckConstraint('xp_per_rep > 0', name='check_xp_per_rep_positive'),
        # Ensure unique movement names within the same node
        Index('idx_movements_node_name_unique', 'node_id', 'name', unique=True),
    )
    
    def __repr__(self):
        return f"<Movement(name='{self.name}', node_id={self.node_id})>"