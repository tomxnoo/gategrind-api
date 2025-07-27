"""
DungeonTrial SQLAlchemy model for V2 database schema.
This model tracks individual trial attempts within dungeon sessions.
"""
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Text, Float, Index, CheckConstraint
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSON
from datetime import datetime
from typing import Optional
from .base import BaseModel


class DungeonTrial(BaseModel):
    """
    DungeonTrial model - Tracks individual trial attempts within dungeon sessions.
    
    Fields:
    - session_id: The dungeon session this trial belongs to
    - trial_number: Sequential number of this trial within the session
    - trial_type: Type of trial (movement-based, etc.)
    - movement_id: The specific movement for this trial
    - required_reps: Target reps to achieve
    - completed_reps: Current progress towards target
    - trial_status: Current status of the trial
    - is_completed: Whether this trial has been completed
    - started_at: When the trial was started
    - completed_at: When the trial was completed (if applicable)
    - trial_data: Additional trial configuration data
    """
    __tablename__ = 'dungeon_trials'
    
    session_id: Mapped[int] = mapped_column(ForeignKey('dungeon_sessions.id', ondelete="CASCADE"), nullable=False)
    trial_number: Mapped[int] = mapped_column(nullable=False)
    trial_type: Mapped[str] = mapped_column(String(50), nullable=False)
    movement_id: Mapped[Optional[int]] = mapped_column(nullable=True)
    required_reps: Mapped[int] = mapped_column(nullable=False)
    completed_reps: Mapped[int] = mapped_column(default=0, nullable=False)
    trial_status: Mapped[str] = mapped_column(String(20), default='pending', nullable=False)
    is_completed: Mapped[bool] = mapped_column(default=False, nullable=False)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    trial_data: Mapped[Optional[dict]] = mapped_column(JSON)
    
    # Relationships
    session: Mapped["DungeonSession"] = relationship("DungeonSession", back_populates="trials")
    
    __table_args__ = (
        CheckConstraint("trial_number > 0", name='check_trial_number_positive'),
        CheckConstraint("required_reps > 0", name='check_required_reps_positive'),
        CheckConstraint("completed_reps >= 0", name='check_completed_reps_non_negative'),
        CheckConstraint("trial_status IN ('pending', 'active', 'completed', 'failed')", name='check_trial_status'),
        Index('idx_dungeon_trials_session', 'session_id'),
        Index('idx_dungeon_trials_number', 'trial_number'),
        Index('idx_dungeon_trials_type', 'trial_type'),
        Index('idx_dungeon_trials_status', 'trial_status'),
        Index('idx_dungeon_trials_completed', 'is_completed'),
        Index('idx_dungeon_trials_started', 'started_at'),
    )
    
    def __repr__(self):
        return f"<DungeonTrial(session_id={self.session_id}, trial_number={self.trial_number}, required_reps={self.required_reps})>"
    
    @property
    def completion_percentage(self) -> float:
        """Calculate trial completion percentage"""
        if self.required_reps == 0:
            return 0.0
        return min(100.0, (self.completed_reps / self.required_reps) * 100.0)
    
    @property
    def is_successful(self) -> bool:
        """Check if trial was completed successfully"""
        return self.is_completed and self.completed_reps >= self.required_reps