"""
Cache Service for Performance Optimization

This service provides caching functionality for frequently accessed data
in the awakening system and other performance-critical operations.
"""

import json
import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, asdict
import asyncio
from functools import wraps

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """Represents a cache entry with metadata"""
    key: str
    value: Any
    created_at: datetime
    expires_at: Optional[datetime] = None
    access_count: int = 0
    last_accessed: Optional[datetime] = None


class CacheService:
    """
    In-memory cache service with TTL support and performance monitoring
    
    Features:
    - TTL (Time To Live) support
    - LRU eviction when cache is full
    - Performance metrics
    - Async-safe operations
    - JSON serialization for complex objects
    """
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        """
        Initialize cache service
        
        Args:
            max_size: Maximum number of entries to store
            default_ttl: Default TTL in seconds
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = asyncio.Lock()
        
        # Performance metrics
        self.hits = 0
        self.misses = 0
        self.evictions = 0
        
    async def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/expired
        """
        async with self._lock:
            entry = self._cache.get(key)
            
            if not entry:
                self.misses += 1
                return None
            
            # Check if expired
            if entry.expires_at and datetime.now(timezone.utc) > entry.expires_at:
                del self._cache[key]
                self.misses += 1
                return None
            
            # Update access metadata
            entry.access_count += 1
            entry.last_accessed = datetime.now(timezone.utc)
            self.hits += 1
            
            return entry.value
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        ttl: Optional[int] = None
    ) -> None:
        """
        Set value in cache
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: TTL in seconds (uses default if None)
        """
        async with self._lock:
            # Calculate expiration
            ttl = ttl or self.default_ttl
            expires_at = datetime.now(timezone.utc) + timedelta(seconds=ttl) if ttl > 0 else None
            
            # Create cache entry
            entry = CacheEntry(
                key=key,
                value=value,
                created_at=datetime.now(timezone.utc),
                expires_at=expires_at
            )
            
            # Check if we need to evict entries
            if len(self._cache) >= self.max_size and key not in self._cache:
                await self._evict_lru()
            
            self._cache[key] = entry
    
    async def delete(self, key: str) -> bool:
        """
        Delete entry from cache
        
        Args:
            key: Cache key
            
        Returns:
            True if key existed, False otherwise
        """
        async with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False
    
    async def clear(self) -> None:
        """Clear all cache entries"""
        async with self._lock:
            self._cache.clear()
            self.hits = 0
            self.misses = 0
            self.evictions = 0
    
    async def get_stats(self) -> Dict[str, Any]:
        """
        Get cache performance statistics
        
        Returns:
            Dict containing cache statistics
        """
        async with self._lock:
            total_requests = self.hits + self.misses
            hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0
            
            return {
                'size': len(self._cache),
                'max_size': self.max_size,
                'hits': self.hits,
                'misses': self.misses,
                'hit_rate': round(hit_rate, 2),
                'evictions': self.evictions
            }
    
    async def cleanup_expired(self) -> int:
        """
        Remove expired entries from cache
        
        Returns:
            Number of entries removed
        """
        async with self._lock:
            now = datetime.now(timezone.utc)
            expired_keys = []
            
            for key, entry in self._cache.items():
                if entry.expires_at and now > entry.expires_at:
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self._cache[key]
            
            return len(expired_keys)
    
    async def _evict_lru(self) -> None:
        """Evict least recently used entry"""
        if not self._cache:
            return
        
        # Find LRU entry
        lru_key = min(
            self._cache.keys(),
            key=lambda k: self._cache[k].last_accessed or self._cache[k].created_at
        )
        
        del self._cache[lru_key]
        self.evictions += 1
    
    # Awakening-specific cache methods
    
    async def cache_user_movements(self, user_id: int, movements: List[Dict[str, Any]], ttl: int = 1800) -> None:
        """Cache user's available movements for quest generation"""
        key = f"user_movements:{user_id}"
        await self.set(key, movements, ttl)
    
    async def get_user_movements(self, user_id: int) -> Optional[List[Dict[str, Any]]]:
        """Get cached user movements"""
        key = f"user_movements:{user_id}"
        return await self.get(key)
    
    async def cache_user_progression(self, user_id: int, progression_data: Dict[str, Any], ttl: int = 900) -> None:
        """Cache user progression data"""
        key = f"user_progression:{user_id}"
        await self.set(key, progression_data, ttl)
    
    async def get_user_progression(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get cached user progression data"""
        key = f"user_progression:{user_id}"
        return await self.get(key)
    
    async def cache_daily_session(self, user_id: int, session_data: Dict[str, Any], ttl: int = 3600) -> None:
        """Cache daily session data"""
        key = f"daily_session:{user_id}:{datetime.now().date()}"
        await self.set(key, session_data, ttl)
    
    async def get_daily_session(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get cached daily session data"""
        key = f"daily_session:{user_id}:{datetime.now().date()}"
        return await self.get(key)
    
    async def invalidate_user_cache(self, user_id: int) -> None:
        """Invalidate all cache entries for a specific user"""
        async with self._lock:
            keys_to_delete = []
            for key in self._cache.keys():
                if f":{user_id}" in key or f":{user_id}:" in key:
                    keys_to_delete.append(key)
            
            for key in keys_to_delete:
                del self._cache[key]


def cache_result(ttl: int = 3600, key_prefix: str = ""):
    """
    Decorator for caching function results
    
    Args:
        ttl: Time to live in seconds
        key_prefix: Prefix for cache key
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            cache_key = f"{key_prefix}{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache (assumes cache_service is available in context)
            if hasattr(wrapper, 'cache_service'):
                cached_result = await wrapper.cache_service.get(cache_key)
                if cached_result is not None:
                    return cached_result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            
            if hasattr(wrapper, 'cache_service'):
                await wrapper.cache_service.set(cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator


# Global cache instance (can be configured per environment)
cache_service = CacheService(max_size=2000, default_ttl=3600)