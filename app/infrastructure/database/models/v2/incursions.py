"""
V2 Database models for incursions system
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Float, JSON, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from enum import Enum

from .base import BaseModel


class IncursionType(str, Enum):
    """Incursion type enumeration"""
    SURGE = "surge"        # System-wide buffs
    CHALLENGE = "challenge"  # Specific tasks
    ANOMALY = "anomaly"    # Rule-changing modifiers


class RewardType(str, Enum):
    """Reward type enumeration"""
    XP = "xp"
    BUFF = "buff"
    ITEM = "item"


class IncursionStatus(str, Enum):
    """Incursion status enumeration"""
    ACTIVE = "active"
    COMPLETED = "completed"
    EXPIRED = "expired"


class Incursion(BaseModel):
    """
    V2 Incursion model for managing group challenge events
    """
    __tablename__ = "incursions_v2"
    
    # Core identification
    incursion_id = Column(String(50), unique=True, nullable=False, index=True)
    
    # Basic information
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    incursion_type = Column(SQLEnum(IncursionType), nullable=False)
    status = Column(SQLEnum(IncursionStatus), default=IncursionStatus.ACTIVE, nullable=False)
    
    # Exercise and progress tracking
    target_exercise = Column(String(100), nullable=False)
    target_reps = Column(Integer, nullable=False)
    current_reps = Column(Integer, default=0, nullable=False)
    
    # Reward information
    reward_type = Column(SQLEnum(RewardType), nullable=False)
    reward_value = Column(Integer, nullable=False)
    reward_description = Column(String(500), nullable=False)
    
    # Timing
    expires_at = Column(DateTime(timezone=True), nullable=False)
    
    # Extra data for extensibility
    extra_data = Column(JSON, default=dict, nullable=False)
    
    # Relationships
    participants = relationship("IncursionParticipant", back_populates="incursion", cascade="all, delete-orphan")
    
    def __init__(self, **kwargs):
        """Initialize incursion with default values"""
        super().__init__(**kwargs)
        if self.current_reps is None:
            self.current_reps = 0
        if self.status is None:
            self.status = IncursionStatus.ACTIVE
    
    @property
    def is_active(self) -> bool:
        """Check if incursion is currently active"""
        return (self.status == IncursionStatus.ACTIVE and 
                not self.is_expired and 
                not self.is_completed)
    
    @property
    def progress_percentage(self) -> float:
        """Calculate completion percentage"""
        if self.target_reps == 0:
            return 0.0
        current = self.current_reps or 0  # Handle None values
        return (current / self.target_reps) * 100
    
    @property
    def is_completed(self) -> bool:
        """Check if incursion is completed"""
        current = self.current_reps or 0  # Handle None values
        return current >= self.target_reps
    
    @property
    def is_expired(self) -> bool:
        """Check if incursion has expired"""
        from datetime import datetime, timezone
        return datetime.now(timezone.utc) > self.expires_at
    
    @property
    def participants_count(self) -> int:
        """Get number of participants"""
        return len(self.participants) if self.participants else 0


class IncursionParticipant(BaseModel):
    """
    V2 model for tracking user participation in incursions
    """
    __tablename__ = "incursion_participants_v2"
    
    # Foreign keys
    incursion_id = Column(Integer, ForeignKey("incursions_v2.id"), nullable=False)
    user_id = Column(Integer, nullable=False)  # Reference to ascendants table
    
    # Participation tracking
    reps_contributed = Column(Integer, default=0, nullable=False)
    participated_at = Column(DateTime(timezone=True), nullable=False)
    
    # Relationships
    incursion = relationship("Incursion", back_populates="participants")
    
    # Composite index for efficient lookups
    __table_args__ = (
        {"extend_existing": True}
    )