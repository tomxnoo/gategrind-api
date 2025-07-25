"""Awakening System Database Models

This module contains SQLAlchemy models for the awakening system,
including daily sessions, quests, and progress tracking.
"""
from datetime import datetime, date
from typing import Optional, Dict, Any
from sqlalchemy import Column, Integer, String, DateTime, Date, Boolean, Text, JSON, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

from app.infrastructure.database.models.v2.base import Base


class AwakeningSession(Base):
    """
    Model for daily awakening sessions.
    Each user gets one session per day that contains multiple quests.
    """
    __tablename__ = "awakening_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("ascendants.id"), nullable=False, index=True)
    session_date = Column(Date, nullable=False, index=True)
    tier_level = Column(String(20), nullable=False, default="normal")  # normal, reduced
    status = Column(String(20), nullable=False, default="active", index=True)  # active, completed
    reset_used = Column(Boolean, nullable=False, default=False)
    reset_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    quests = relationship(
    "AwakeningQuest",
    back_populates="session",
    cascade="all, delete-orphan",
    lazy="selectin"
)
    rewards = relationship("AwakeningReward", back_populates="session", cascade="all, delete-orphan", lazy="selectin")
    ascendant = relationship("Ascendant", back_populates="awakening_sessions")

    # Indexes for efficient querying
    __table_args__ = (
        Index('idx_awakening_sessions_user_date', 'user_id', 'session_date'),
        Index('idx_awakening_sessions_status', 'status'),
    )


class AwakeningQuest(Base):
    """
    Model for individual quests within an awakening session.
    Each quest has specific targets and tracks completion progress.
    """
    __tablename__ = "awakening_quests"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("awakening_sessions.id"), nullable=False, index=True)
    quest_type = Column(String(50), nullable=False, index=True)  # movement_reps, time_based, distance
    target_movement_id = Column(Integer, nullable=True)  # Foreign key to movements table
    target_movement = Column(String(100), nullable=True)  # e.g., "Standard Pushup" (for display)
    target_reps = Column(Integer, nullable=True)
    target_time = Column(Integer, nullable=True)  # in seconds
    target_distance = Column(Integer, nullable=True)  # in meters
    difficulty_level = Column(String(20), nullable=False, default="moderate")  # easy, moderate, hard
    parameters = Column(JSON, nullable=True)  # Additional quest parameters
    status = Column(String(20), nullable=False, default="active", index=True)  # active, completed
    progress_reps = Column(Integer, nullable=False, default=0)
    progress_time = Column(Integer, nullable=False, default=0)  # in seconds
    progress_distance = Column(Integer, nullable=False, default=0)  # in meters
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    session = relationship("AwakeningSession", back_populates="quests")
    progress_entries = relationship("UserAwakeningProgress", back_populates="quest", cascade="all, delete-orphan")

    # Indexes for efficient querying
    __table_args__ = (
        Index('idx_awakening_quests_session', 'session_id'),
        Index('idx_awakening_quests_type_status', 'quest_type', 'status'),
        Index('idx_awakening_quests_movement', 'target_movement_id'),
    )


class AwakeningReward(Base):
    """
    Model for tracking rewards earned from awakening session completion.
    """
    __tablename__ = "awakening_rewards"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("awakening_sessions.id"), nullable=False, index=True)
    shadow_keys = Column(Integer, nullable=False, default=0)
    xp_gained = Column(Integer, nullable=False, default=0)
    stat_points = Column(Integer, nullable=False, default=0)
    aura_change = Column(Integer, nullable=False, default=0)
    streak_bonus = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    session = relationship("AwakeningSession", back_populates="rewards")

    # Indexes for efficient querying
    __table_args__ = (
        Index('idx_awakening_rewards_session', 'session_id'),
    )


class UserAwakeningProgress(Base):
    """
    Model for tracking detailed progress on individual awakening quests.
    This allows for real-time progress updates and validation.
    """
    __tablename__ = "user_awakening_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    quest_id = Column(Integer, ForeignKey("awakening_quests.id"), nullable=False, index=True)
    progress_reps = Column(Integer, nullable=False, default=0)
    progress_time = Column(Integer, nullable=False, default=0)  # in seconds
    progress_distance = Column(Integer, nullable=False, default=0)  # in meters
    last_updated = Column(DateTime, nullable=False, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    rewards_claimed = Column(Boolean, nullable=False, default=False)

    # Relationships
    quest = relationship("AwakeningQuest", back_populates="progress_entries")

    # Indexes for efficient querying
    __table_args__ = (
        Index('idx_user_awakening_progress_user_quest', 'user_id', 'quest_id'),
        Index('idx_user_awakening_progress_completed', 'completed_at'),
    )