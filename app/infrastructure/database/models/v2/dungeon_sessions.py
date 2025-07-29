"""
DungeonSession SQLAlchemy model for V2 database schema.
This model tracks active dungeon runs and session state management.
"""
from sqlalchemy import Column, Integer, BigInteger, String, DateTime, Boolean, Text, ForeignKey, Index
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSON
from datetime import datetime, timedelta, UTC
from typing import Optional, List, Dict, Any
from .base import BaseModel


class DungeonSession(BaseModel):
    """
    Tracks active dungeon runs for ascendants.
    Each session represents a single dungeon attempt with multiple trials.
    """
    __tablename__ = "dungeon_sessions"
    
    # Core session data
    ascendant_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("ascendants.id"), nullable=False, index=True)
    dungeon_level: Mapped[int] = mapped_column(nullable=False, index=True)
    shadow_keys_spent: Mapped[int] = mapped_column(nullable=False)
    status: Mapped[str] = mapped_column("session_status", String(20), default="active", nullable=False)
    
    # Trial data as JSON
    trial_data: Mapped[Optional[dict]] = mapped_column(JSON)
    
    # Daily modifier relationship
    daily_modifier_id: Mapped[Optional[int]] = mapped_column(ForeignKey("daily_modifiers.id"))
    
    # Timing
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(UTC) + timedelta(hours=24)
    )
    
    # Relationships
    ascendant: Mapped["Ascendant"] = relationship("Ascendant", back_populates="dungeon_sessions")
    trials: Mapped[List["DungeonTrial"]] = relationship("DungeonTrial", back_populates="session", cascade="all, delete-orphan")
    rewards: Mapped[List["DungeonReward"]] = relationship("DungeonReward", back_populates="session")
    daily_modifier: Mapped[Optional["DailyModifier"]] = relationship("DailyModifier")
    
    __table_args__ = (
        Index('idx_dungeon_sessions_ascendant', 'ascendant_id'),
        Index('idx_dungeon_sessions_level', 'dungeon_level'),
        Index('idx_dungeon_sessions_status', 'session_status'),
        Index('idx_dungeon_sessions_expires', 'expires_at'),
        Index('idx_dungeon_sessions_keys_spent', 'shadow_keys_spent'),
    )
    
    def __repr__(self):
        return f"<DungeonSession(ascendant_id={self.ascendant_id}, level={self.dungeon_level}, status='{self.status}')>"
    
    @property
    def is_completed(self) -> bool:
        """Check if the session is completed successfully"""
        return self.status == 'completed'
    
    @property
    def is_expired(self) -> bool:
        """Check if the session has expired"""
        return datetime.now(UTC) > self.expires_at
    
    @property
    def is_active(self) -> bool:
        """Check if the session is currently active"""
        return self.status == 'active' and not self.is_expired