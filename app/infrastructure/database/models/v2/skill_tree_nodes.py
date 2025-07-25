"""
SkillTreeNode SQLAlchemy model for V2 database schema.

This model represents individual nodes in the skill tree progression system.
Each node represents a specific level within a movement category and contains
the movements/exercises available at that progression level.
"""
from sqlalchemy import Column, String, Integer, Text, ForeignKey, Index, CheckConstraint
from sqlalchemy.orm import relationship

from .base import BaseModel

class SkillTreeNode(BaseModel):
    """
    SkillTreeNode model - Individual progression steps within movement categories.
    
    Each node represents a specific level (1-5) within a movement category and
    defines the unlock requirements and available movements for that progression tier.
    
    Fields:
    - category_id: Foreign key to MovementCategory (string-based)
    - level: Progression level within the category (1-5)
    - name: Display name for this progression level (e.g., "Foundation", "First Ascent")
    - description: Detailed description of this progression level
    - required_ascendant_level: Minimum Ascendant level required to unlock
    - required_str_points: Strength points cost to unlock this node
    - required_end_points: Endurance points cost to unlock this node  
    - required_tech_points: Technique points cost to unlock this node
    """
    __tablename__ = 'skill_tree_nodes'
    
    # Core identification
    node_id = Column(String(50), unique=True, nullable=False, index=True)  # String-based identifier from config
    category_id = Column(String(50), ForeignKey('movement_categories.id'), nullable=False)
    level = Column(Integer, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    
    # Unlock requirements
    required_ascendant_level = Column(Integer, default=1, nullable=False)
    required_str_points = Column(Integer, default=0, nullable=False)
    required_end_points = Column(Integer, default=0, nullable=False)
    required_tech_points = Column(Integer, default=0, nullable=False)
    
    # Relationships
    category = relationship("MovementCategory", back_populates="skill_tree_nodes")
    movements = relationship("Movement", back_populates="node", cascade="all, delete-orphan")
    user_progress = relationship("UserSkillProgress", back_populates="node", cascade="all, delete-orphan")
    
    # Indexes and Constraints for performance and data integrity
    __table_args__ = (
        # Unique constraint ensures no duplicate category/level combinations
        Index('idx_skill_tree_nodes_category_level_unique', 'category_id', 'level', unique=True),
        
        # Performance index for level-based queries
        Index('idx_skill_tree_nodes_level', 'level'),
        
        # Data integrity constraints
        CheckConstraint('level >= 1 AND level <= 5', name='check_level_range'),
        CheckConstraint('required_ascendant_level >= 1', name='check_required_ascendant_level_positive'),
        CheckConstraint('required_str_points >= 0', name='check_required_str_points_non_negative'),
        CheckConstraint('required_end_points >= 0', name='check_required_end_points_non_negative'),
        CheckConstraint('required_tech_points >= 0', name='check_required_tech_points_non_negative'),
    )
    
    def __repr__(self):
        return f"<SkillTreeNode(category='{self.category_id}', level={self.level}, name='{self.name}')>"