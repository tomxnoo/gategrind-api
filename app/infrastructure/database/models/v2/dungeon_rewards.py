"""
DungeonReward SQLAlchemy model for V2 database schema.
This model tracks rewards earned from dungeon completion.
"""
from sqlalchemy import Column, Integer, BigInteger, String, ForeignKey, DateTime, Boolean, Float, Index, CheckConstraint
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime
from typing import Optional
from .base import BaseModel


class DungeonReward(BaseModel):
    """
    DungeonReward model - Tracks rewards earned from dungeon completion.
    
    Fields:
    - session_id: The dungeon session that earned this reward
    - ascendant_id: The user who earned this reward
    - reward_type: Type of reward earned (aura, stat_points, shadow_keys)
    - amount: Amount/quantity of the reward
    - applied_at: When the reward was applied to the user
    """
    __tablename__ = 'dungeon_rewards'
    
    session_id: Mapped[int] = mapped_column(ForeignKey('dungeon_sessions.id', ondelete="CASCADE"), nullable=False)
    ascendant_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('ascendants.id', ondelete="CASCADE"), nullable=False)
    reward_type: Mapped[str] = mapped_column(String(20), nullable=False)
    amount: Mapped[int] = mapped_column(nullable=False)
    applied_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # Relationships
    session: Mapped["DungeonSession"] = relationship("DungeonSession", back_populates="rewards")
    ascendant: Mapped["Ascendant"] = relationship("Ascendant", back_populates="dungeon_rewards")
    
    __table_args__ = (
        CheckConstraint("reward_type IN ('aura', 'stat_points', 'shadow_keys')", name='check_reward_type'),
        Index('idx_dungeon_rewards_session', 'session_id'),
        Index('idx_dungeon_rewards_ascendant', 'ascendant_id'),
        Index('idx_dungeon_rewards_type', 'reward_type'),
        Index('idx_dungeon_rewards_applied', 'applied_at'),
    )
    
    def __repr__(self):
        return f"<DungeonReward(ascendant_id={self.ascendant_id}, type='{self.reward_type}', amount={self.amount})>"