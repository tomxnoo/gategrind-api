"""
AscendantStats SQLAlchemy model for V2 database schema.
This model tracks the individual level and experience points for each of
the three core stats (STR, END, TECH), forming a one-to-one relationship
with the Ascendant model.
"""
from sqlalchemy import Column, Integer, Float, ForeignKey, Index, CheckConstraint
from sqlalchemy.orm import relationship

from .base import BaseModel

class AscendantStats(BaseModel):
    """
    AscendantStats model - Tracks granular progression for STR, END, and TECH.

    Fields:
    - ascendant_id: Foreign key to the Ascendant model.
    - str_level / str_xp: Tracks Strength progression.
    - end_level / end_xp: Tracks Endurance progression.
    - tech_level / tech_xp: Tracks Technique progression.
    """
    __tablename__ = 'ascendant_stats'

    ascendant_id = Column(Integer, ForeignKey('ascendants.id', ondelete='CASCADE'), unique=True, nullable=False)

    # Strength progression
    str_level = Column(Integer, default=1, nullable=False)
    str_xp = Column(Float, default=0.0, nullable=False)

    # Endurance progression
    end_level = Column(Integer, default=1, nullable=False)
    end_xp = Column(Float, default=0.0, nullable=False)

    # Technique progression
    tech_level = Column(Integer, default=1, nullable=False)
    tech_xp = Column(Float, default=0.0, nullable=False)

    # Relationships
    ascendant = relationship("Ascendant", back_populates="stats")

    # Indexes and Constraints for performance and data integrity
    __table_args__ = (
        Index('idx_ascendant_stats_ascendant_id', 'ascendant_id'),
        CheckConstraint('str_level >= 1', name='check_str_level_positive'),
        CheckConstraint('str_xp >= 0', name='check_str_xp_non_negative'),
        CheckConstraint('end_level >= 1', name='check_end_level_positive'),
        CheckConstraint('end_xp >= 0', name='check_end_xp_non_negative'),
        CheckConstraint('tech_level >= 1', name='check_tech_level_positive'),
        CheckConstraint('tech_xp >= 0', name='check_tech_xp_non_negative'),
    )

    def __repr__(self):
        return f"<AscendantStats(ascendant_id={self.ascendant_id}, STR={self.str_level}, END={self.end_level}, TECH={self.tech_level})>"