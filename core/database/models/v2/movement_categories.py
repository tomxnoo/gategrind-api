"""
MovementCategory SQLAlchemy model for V2 database schema.
This model represents the high-level categories for all movements.
It is a static data table, pre-populated with the 18 core categories.
"""
from sqlalchemy import Column, String, Enum
from sqlalchemy.orm import relationship

from .base import BaseModel

class MovementCategory(BaseModel):
    """
    MovementCategory model - A high-level grouping for movements.

    Inherits from BaseModel but overrides the 'id' to use a string-based
    primary key, while retaining the standard created_at/updated_at fields.
    Fields:
    - id: A unique string identifier (e.g., 'PULL_VERTICAL').
    - name: The human-readable name (e.g., 'Vertical Pulling').
    - primary_stat: The core stat (STR, END, TECH) associated with this category.
    """
    __tablename__ = 'movement_categories'
    
    # Override the integer ID from BaseModel with a string-based primary key
    id = Column(String(50), primary_key=True, unique=True, nullable=False)
    name = Column(String(100), unique=True, nullable=False)
    primary_stat = Column(Enum('STR', 'END', 'TECH', name='stat_enum'), nullable=False)
    
    # Relationships to other tables
    movements = relationship("Movement", back_populates="category", cascade="all, delete-orphan")
    skill_tree_nodes = relationship("SkillTreeNode", back_populates="category", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<MovementCategory(id='{self.id}', name='{self.name}')>"