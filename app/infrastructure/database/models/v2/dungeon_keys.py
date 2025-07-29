"""
DungeonKey SQLAlchemy model for V2 database schema.
This model manages the Shadow Keys that users earn and consume for dungeon entry.
"""
from sqlalchemy import Column, Integer, BigInteger, String, ForeignKey, Index
from sqlalchemy.orm import relationship

from .base import BaseModel


class DungeonKey(BaseModel):
    """
    DungeonKey model - Manages the keys users earn for dungeon access.
    
    Fields:
    - ascendant_id: The user who owns these keys.
    - key_type: The type of key (e.g., 'shadow_key').
    - quantity: How many keys of this type the user has.
    """
    __tablename__ = 'dungeon_keys'
    
    ascendant_id = Column(BigInteger, ForeignKey('ascendants.id', ondelete="CASCADE"), nullable=False)
    key_type = Column(String(50), nullable=False, default='shadow_key')  # 'shadow_key', future key types
    quantity = Column(Integer, nullable=False, default=0)
    
    # Relationships
    ascendant = relationship("Ascendant", back_populates="dungeon_keys")
    
    __table_args__ = (
        Index('idx_dungeon_keys_ascendant_type', 'ascendant_id', 'key_type'),
    )
    
    def __repr__(self):
        return f"<DungeonKey(ascendant_id={self.ascendant_id}, key_type='{self.key_type}', quantity={self.quantity})>"