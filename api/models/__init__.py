"""
Pydantic models for the Realm of Shadows API
"""

from .common import (
    ResponseStatus,
    BaseResponse,
    SuccessResponse,
    ErrorResponse,
    PaginationParams,
    PaginatedResponse
)
from .user import UserProfile, UserStats, UserPreferences
from .quest import QuestData, QuestResponse, QuestCompletion
from .buff import BuffData, BuffResponse, ActiveBuff
from .incursion import IncursionData, IncursionResponse
from .auth import LoginRequest, TokenResponse
from .awakening import AwakeningSession, AwakeningResponse