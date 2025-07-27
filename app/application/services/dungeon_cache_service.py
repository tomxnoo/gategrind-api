"""
DungeonCacheService - Caching layer for dungeon system performance optimization

This service provides caching for:
- Daily modifiers
- Skill tree validation results
- Dungeon level requirements
- Shadow key balances
"""
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, List
from functools import lru_cache
import asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.base_service import BaseService
from app.infrastructure.database.models.v2.daily_modifiers import DailyModifier
from app.infrastructure.database.models.v2.dungeon_level_unlocks import DungeonLevelUnlock


class DungeonCacheService(BaseService):
    """
    Caching service for dungeon system performance optimization.
    
    Provides in-memory caching for frequently accessed data with TTL support.
    """
    
    def __init__(self, session: Optional[AsyncSession] = None):
        """Initialize the cache service."""
        super().__init__(session)
        self._daily_modifier_cache: Optional[Dict[str, Any]] = None
        self._daily_modifier_cache_time: Optional[datetime] = None
        self._skill_tree_cache: Dict[str, Any] = {}
        self._level_requirements_cache: Dict[int, Dict[str, Any]] = {}
        self._cache_ttl = timedelta(minutes=15)  # 15-minute TTL for most caches
        self._daily_modifier_ttl = timedelta(hours=1)  # 1-hour TTL for daily modifiers
    
    async def get_cached_daily_modifier(self) -> Optional[DailyModifier]:
        """
        Get cached daily modifier with TTL validation.
        
        Returns:
            DailyModifier or None if no active modifier
        """
        try:
            # Check if cache is valid
            if (self._daily_modifier_cache is None or 
                self._daily_modifier_cache_time is None or
                datetime.now(timezone.utc) - self._daily_modifier_cache_time > self._daily_modifier_ttl):
                
                # Refresh cache
                await self._refresh_daily_modifier_cache()
            
            if self._daily_modifier_cache and self._daily_modifier_cache.get('modifier'):
                # Convert cached data back to DailyModifier object
                modifier_data = self._daily_modifier_cache['modifier']
                modifier = DailyModifier(**modifier_data)
                return modifier
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting cached daily modifier: {e}")
            # Fallback to direct database query
            return await self._get_daily_modifier_from_db()
    
    async def _refresh_daily_modifier_cache(self):
        """Refresh the daily modifier cache from database."""
        try:
            modifier = await self._get_daily_modifier_from_db()
            
            if modifier:
                # Cache the modifier data as dict
                self._daily_modifier_cache = {
                    'modifier': {
                        'id': modifier.id,
                        'modifier_date': modifier.modifier_date,
                        'modifier_name': modifier.modifier_name,
                        'modifier_type': modifier.modifier_type,
                        'difficulty_multiplier': float(modifier.difficulty_multiplier),
                        'reward_multiplier': float(modifier.reward_multiplier),
                        'xp_bonus': float(modifier.xp_bonus),
                        'skill_point_bonus': float(modifier.skill_point_bonus),
                        'description': modifier.description,
                        'is_active': modifier.is_active,
                        'modifier_data': modifier.modifier_data,
                        'created_at': modifier.created_at
                    }
                }
            else:
                self._daily_modifier_cache = {'modifier': None}
            
            self._daily_modifier_cache_time = datetime.now(timezone.utc)
            
        except Exception as e:
            self.logger.error(f"Error refreshing daily modifier cache: {e}")
            self._daily_modifier_cache = {'modifier': None}
            self._daily_modifier_cache_time = datetime.now(timezone.utc)
    
    async def _get_daily_modifier_from_db(self) -> Optional[DailyModifier]:
        """Get daily modifier directly from database."""
        try:
            session = await self.get_session()
            today = datetime.now(timezone.utc).date()
            
            result = await session.execute(
                select(DailyModifier).where(DailyModifier.modifier_date == today)
            )
            return result.scalar_one_or_none()
            
        except Exception as e:
            self.logger.error(f"Error getting daily modifier from database: {e}")
            return None
    
    @lru_cache(maxsize=128)
    def get_cached_aura_requirement(self, level: int) -> int:
        """
        Get cached aura requirement calculation.
        
        Args:
            level: Dungeon level
            
        Returns:
            Required aura amount
        """
        base_aura = 100
        return int(base_aura * (1.5 ** (level - 1)))
    
    @lru_cache(maxsize=128)
    def get_cached_stat_requirements(self, level: int) -> Dict[str, int]:
        """
        Get cached stat requirements calculation.
        
        Args:
            level: Dungeon level
            
        Returns:
            Dict with strength, endurance, technique requirements
        """
        base_stat = 10
        multiplier = 1.5
        required_value = int(base_stat * (multiplier ** (level - 1)))
        
        return {
            'strength': required_value,
            'endurance': required_value,
            'technique': required_value
        }
    
    @lru_cache(maxsize=128)
    def get_cached_skill_tree_requirements(self, level: int) -> int:
        """
        Get cached skill tree requirements calculation.
        
        Args:
            level: Dungeon level
            
        Returns:
            Required number of Movement skill tree nodes
        """
        if level <= 1:
            return 0
        elif level <= 5:
            return level - 1
        elif level <= 10:
            return 5 + (level - 5) * 2
        else:
            return 15 + (level - 10) * 3
    
    async def get_cached_level_requirements(self, level: int) -> Optional[Dict[str, Any]]:
        """
        Get cached level unlock requirements.
        
        Args:
            level: Dungeon level
            
        Returns:
            Dict with level requirements or None if not found
        """
        try:
            # Check cache first
            if level in self._level_requirements_cache:
                cached_data = self._level_requirements_cache[level]
                # Check if cache is still valid
                if datetime.now(timezone.utc) - cached_data['cached_at'] < self._cache_ttl:
                    return cached_data['requirements']
            
            # Refresh from database
            session = await self.get_session()
            result = await session.execute(
                select(DungeonLevelUnlock).where(
                    DungeonLevelUnlock.dungeon_level == level
                )
            )
            unlock_req = result.scalar_one_or_none()
            
            if unlock_req:
                requirements = {
                    'dungeon_level': unlock_req.dungeon_level,
                    'required_ascendant_level': unlock_req.required_ascendant_level,
                    'required_aura': unlock_req.required_aura,
                    'required_skill_tree_progress': unlock_req.required_skill_tree_progress,
                    'required_previous_completion': unlock_req.required_previous_completion,
                    'unlock_description': unlock_req.unlock_description,
                    'is_enabled': unlock_req.is_enabled
                }
                
                # Cache the requirements
                self._level_requirements_cache[level] = {
                    'requirements': requirements,
                    'cached_at': datetime.now(timezone.utc)
                }
                
                return requirements
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting cached level requirements for level {level}: {e}")
            return None
    
    def invalidate_daily_modifier_cache(self):
        """Invalidate the daily modifier cache."""
        self._daily_modifier_cache = None
        self._daily_modifier_cache_time = None
    
    def invalidate_level_requirements_cache(self, level: Optional[int] = None):
        """
        Invalidate level requirements cache.
        
        Args:
            level: Specific level to invalidate, or None to clear all
        """
        if level is not None:
            self._level_requirements_cache.pop(level, None)
        else:
            self._level_requirements_cache.clear()
    
    def clear_all_caches(self):
        """Clear all caches."""
        self._daily_modifier_cache = None
        self._daily_modifier_cache_time = None
        self._skill_tree_cache.clear()
        self._level_requirements_cache.clear()
        
        # Clear LRU caches
        self.get_cached_aura_requirement.cache_clear()
        self.get_cached_stat_requirements.cache_clear()
        self.get_cached_skill_tree_requirements.cache_clear()
    
    async def warm_up_caches(self, levels: List[int] = None):
        """
        Warm up caches for specified levels.
        
        Args:
            levels: List of levels to warm up, defaults to 1-20
        """
        try:
            if levels is None:
                levels = list(range(1, 21))  # Warm up levels 1-20
            
            # Warm up daily modifier cache
            await self.get_cached_daily_modifier()
            
            # Warm up level requirements cache
            for level in levels:
                await self.get_cached_level_requirements(level)
                # Also warm up calculation caches
                self.get_cached_aura_requirement(level)
                self.get_cached_stat_requirements(level)
                self.get_cached_skill_tree_requirements(level)
            
            self.logger.info(f"Warmed up caches for levels: {levels}")
            
        except Exception as e:
            self.logger.error(f"Error warming up caches: {e}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics for monitoring.
        
        Returns:
            Dict with cache hit rates and sizes
        """
        return {
            'daily_modifier_cached': self._daily_modifier_cache is not None,
            'daily_modifier_cache_age': (
                (datetime.now(timezone.utc) - self._daily_modifier_cache_time).total_seconds()
                if self._daily_modifier_cache_time else None
            ),
            'level_requirements_cache_size': len(self._level_requirements_cache),
            'aura_requirement_cache_info': self.get_cached_aura_requirement.cache_info()._asdict(),
            'stat_requirements_cache_info': self.get_cached_stat_requirements.cache_info()._asdict(),
            'skill_tree_requirements_cache_info': self.get_cached_skill_tree_requirements.cache_info()._asdict()
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check for the cache service.
        
        Returns:
            Dict with health check results
        """
        try:
            # Test database connectivity
            session = await self.get_session()
            await session.execute(select(1))
            
            # Get cache statistics
            cache_stats = self.get_cache_stats()
            
            return {
                'status': 'healthy',
                'service': 'DungeonCacheService',
                'database_connection': 'ok',
                'cache_stats': cache_stats,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return {
                'status': 'unhealthy',
                'service': 'DungeonCacheService',
                'error': str(e),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }