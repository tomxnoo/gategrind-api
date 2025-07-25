"""
Awakening System API Schemas

Pydantic models for request and response validation in the awakening system API.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum


class ReadinessLevel(int, Enum):
    """Readiness levels for awakening sessions"""
    VERY_LOW = 1
    LOW = 2
    BELOW_AVERAGE = 3
    AVERAGE = 4
    ABOVE_AVERAGE = 5
    GOOD = 6
    VERY_GOOD = 7
    HIGH = 8
    VERY_HIGH = 9
    PEAK = 10


class QuestType(str, Enum):
    """Types of awakening quests"""
    REPS = "reps"
    DURATION = "duration"
    SETS = "sets"
    DISTANCE = "distance"


class DifficultyTier(str, Enum):
    """Difficulty tiers for quests"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXTREME = "extreme"


class RewardType(str, Enum):
    """Types of rewards"""
    XP = "xp"
    AURA = "aura"
    SHADOW_KEY = "shadow_key"


# Request Models
class AwakeningActionRequest(BaseModel):
    """Request model for creating/getting awakening session"""
    user_id: int = Field(..., gt=0, description="User ID")
    readiness_level: ReadinessLevel = Field(..., description="User's readiness level (1-10)")
    
    @validator('readiness_level')
    def validate_readiness_level(cls, v):
        if not (1 <= v <= 10):
            raise ValueError('Readiness level must be between 1 and 10')
        return v


class QuestCompletionRequest(BaseModel):
    """Request model for quest completion"""
    progress_data: Dict[str, Any] = Field(..., description="User's movement progress data")
    
    @validator('progress_data')
    def validate_progress_data(cls, v):
        if not v:
            raise ValueError('Progress data cannot be empty')
        return v


class AdminResetRequest(BaseModel):
    """Request model for administrative reset"""
    reason: str = Field(..., min_length=10, description="Reason for reset")
    reset_streak: bool = Field(default=False, description="Whether to reset user's streak")
    reset_progress: bool = Field(default=False, description="Whether to reset all progress")


class AdminProgressAdjustmentRequest(BaseModel):
    """Request model for administrative progress adjustment"""
    adjustments: Dict[str, int] = Field(..., description="Progress adjustments to apply")
    reason: str = Field(..., min_length=10, description="Reason for adjustment")


# Response Models
class QuestData(BaseModel):
    """Quest data model"""
    id: int
    movement_id: int
    movement_name: str
    quest_type: QuestType
    target_value: int
    current_progress: int
    is_completed: bool
    difficulty_tier: DifficultyTier
    xp_reward: int
    aura_reward: int
    shadow_key_reward: int
    description: str


class SessionData(BaseModel):
    """Session data model"""
    id: int
    user_id: int
    readiness_level: int
    quest_count: int
    completed_quests: int
    is_completed: bool
    created_at: datetime
    completed_at: Optional[datetime] = None
    quests: List[QuestData]


class RewardData(BaseModel):
    """Reward data model"""
    reward_type: RewardType
    amount: int
    description: str


class ProgressData(BaseModel):
    """User progress data model"""
    current_streak: int
    longest_streak: int
    total_sessions_completed: int
    total_quests_completed: int
    total_xp_earned: int
    total_aura_earned: int
    total_shadow_keys_earned: int
    average_readiness_level: Optional[float] = None


class AwakeningActionResponse(BaseModel):
    """Response model for awakening action"""
    success: bool
    message: str
    session: SessionData
    is_new_session: bool
    next_available_reset: Optional[datetime] = None


class QuestCompletionResponse(BaseModel):
    """Response model for quest completion"""
    success: bool
    message: str
    quest_completed: bool
    session_completed: bool
    rewards_earned: List[RewardData]
    updated_progress: ProgressData
    next_quest_available: bool = True


class AwakeningStatusResponse(BaseModel):
    """Response model for awakening status"""
    user_id: int
    has_active_session: bool
    current_session: Optional[SessionData] = None
    progress: ProgressData
    last_session_date: Optional[datetime] = None
    can_create_new_session: bool


class SessionHistoryItem(BaseModel):
    """Historical session item"""
    id: int
    readiness_level: int
    quest_count: int
    completed_quests: int
    is_completed: bool
    created_at: datetime
    completed_at: Optional[datetime] = None
    completion_time_minutes: Optional[int] = None


class AwakeningHistoryResponse(BaseModel):
    """Response model for awakening history"""
    user_id: int
    total_sessions: int
    sessions: List[SessionHistoryItem]
    progress_summary: ProgressData
    pagination: Dict[str, Any]


class AwakeningResetResponse(BaseModel):
    """Response model for session reset"""
    success: bool
    message: str
    new_session: Optional[SessionData] = None
    reset_timestamp: datetime


class SystemHealthMetrics(BaseModel):
    """System health metrics"""
    total_active_sessions: int
    total_completed_sessions_today: int
    average_completion_rate: float
    system_load: str
    cache_hit_rate: float
    database_status: str


class AwakeningHealthResponse(BaseModel):
    """Response model for system health"""
    status: str
    timestamp: datetime
    metrics: SystemHealthMetrics
    uptime_hours: float


class SystemStatsData(BaseModel):
    """System statistics data"""
    total_users: int
    active_users_today: int
    total_sessions_created: int
    total_sessions_completed: int
    total_quests_completed: int
    average_session_completion_rate: float
    most_popular_readiness_level: int
    total_rewards_distributed: Dict[str, int]


class SystemStatsResponse(BaseModel):
    """Response model for system statistics"""
    timestamp: datetime
    stats: SystemStatsData
    trends: Dict[str, Any]


# Error Response Models
class ErrorDetail(BaseModel):
    """Error detail model"""
    code: str
    message: str
    field: Optional[str] = None


class ErrorResponse(BaseModel):
    """Standard error response model"""
    success: bool = False
    error: str
    details: Optional[List[ErrorDetail]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Configuration Models
class QuestGenerationConfig(BaseModel):
    """Configuration for quest generation"""
    min_quests: int = Field(default=2, ge=1, le=5)
    max_quests: int = Field(default=4, ge=2, le=6)
    difficulty_distribution: Dict[str, float] = Field(
        default={
            "easy": 0.4,
            "medium": 0.4,
            "hard": 0.15,
            "extreme": 0.05
        }
    )
    movement_variety_factor: float = Field(default=0.7, ge=0.0, le=1.0)


class CacheConfig(BaseModel):
    """Configuration for caching"""
    ttl_seconds: int = Field(default=300, ge=60, le=3600)
    max_size: int = Field(default=1000, ge=100, le=10000)
    enable_performance_monitoring: bool = Field(default=True)


class AwakeningSystemConfig(BaseModel):
    """Overall system configuration"""
    quest_generation: QuestGenerationConfig = Field(default_factory=QuestGenerationConfig)
    cache: CacheConfig = Field(default_factory=CacheConfig)
    max_daily_resets: int = Field(default=3, ge=1, le=10)
    streak_reset_threshold_days: int = Field(default=2, ge=1, le=7)
    enable_admin_features: bool = Field(default=True)