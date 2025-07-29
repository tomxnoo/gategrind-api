"""
Enhanced cache management system with Redis integration.

This module provides a comprehensive caching solution with:
- Redis backend support
- Memory fallback for development
- TTL management and cache invalidation
- Performance metrics and monitoring
"""
import json
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union, TypeVar, Generic
from dataclasses import dataclass, asdict
from functools import wraps
import hashlib

try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

from app.core.exceptions import CacheError

logger = logging.getLogger(__name__)

T = TypeVar('T')


@dataclass
class CacheStats:
    """Cache performance statistics."""
    hits: int = 0
    misses: int = 0
    sets: int = 0
    deletes: int = 0
    errors: int = 0
    
    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate."""
        total = self.hits + self.misses
        return (self.hits / total) if total > 0 else 0.0


class CacheManager(Generic[T]):
    """Enhanced cache manager with Redis backend and memory fallback."""
    
    def __init__(
        self,
        redis_url: Optional[str] = None,
        default_ttl: int = 3600,
        key_prefix: str = "ros:",
        enable_memory_fallback: bool = True
    ):
        self.redis_url = redis_url
        self.default_ttl = default_ttl
        self.key_prefix = key_prefix
        self.enable_memory_fallback = enable_memory_fallback
        
        # Redis client
        self._redis: Optional[redis.Redis] = None
        self._redis_available = False
        
        # Memory cache fallback
        self._memory_cache: Dict[str, Any] = {}
        self._memory_expiry: Dict[str, datetime] = {}
        
        # Performance tracking
        self.stats = CacheStats()
        
        # Initialize Redis connection
        if REDIS_AVAILABLE and redis_url:
            self._initialize_redis()
    
    def _initialize_redis(self):
        """Initialize Redis connection."""
        try:
            self._redis = redis.from_url(
                self.redis_url,
                decode_responses=True,
                retry_on_timeout=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            self._redis_available = True
            logger.info("Redis cache initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize Redis: {e}")
            self._redis_available = False
    
    def _make_key(self, key: str) -> str:
        """Create a prefixed cache key."""
        return f"{self.key_prefix}{key}"
    
    def _hash_key(self, data: Any) -> str:
        """Create a hash key from complex data."""
        if isinstance(data, (dict, list)):
            data_str = json.dumps(data, sort_keys=True)
        else:
            data_str = str(data)
        return hashlib.md5(data_str.encode()).hexdigest()
    
    async def get(self, key: str) -> Optional[T]:
        """Get value from cache."""
        cache_key = self._make_key(key)
        
        try:
            # Try Redis first
            if self._redis_available and self._redis:
                value = await self._redis.get(cache_key)
                if value is not None:
                    self.stats.hits += 1
                    return json.loads(value)
            
            # Fallback to memory cache
            if self.enable_memory_fallback:
                if cache_key in self._memory_cache:
                    # Check expiry
                    if cache_key not in self._memory_expiry or self._memory_expiry[cache_key] > datetime.utcnow():
                        self.stats.hits += 1
                        return self._memory_cache[cache_key]
                    else:
                        # Remove expired entry
                        self._memory_cache.pop(cache_key, None)
                        self._memory_expiry.pop(cache_key, None)
            
            self.stats.misses += 1
            return None
            
        except Exception as e:
            self.stats.errors += 1
            logger.error(f"Cache get error for key {key}: {e}")
            return None
    
    async def set(
        self,
        key: str,
        value: T,
        ttl: Optional[int] = None
    ) -> bool:
        """Set value in cache."""
        cache_key = self._make_key(key)
        ttl = ttl or self.default_ttl
        
        try:
            serialized_value = json.dumps(value, default=str)
            
            # Try Redis first
            if self._redis_available and self._redis:
                success = await self._redis.setex(cache_key, ttl, serialized_value)
                if success:
                    self.stats.sets += 1
                    return True
            
            # Fallback to memory cache
            if self.enable_memory_fallback:
                self._memory_cache[cache_key] = value
                self._memory_expiry[cache_key] = datetime.utcnow() + timedelta(seconds=ttl)
                self.stats.sets += 1
                return True
            
            return False
            
        except Exception as e:
            self.stats.errors += 1
            logger.error(f"Cache set error for key {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        cache_key = self._make_key(key)
        
        try:
            deleted = False
            
            # Delete from Redis
            if self._redis_available and self._redis:
                count = await self._redis.delete(cache_key)
                if count > 0:
                    deleted = True
            
            # Delete from memory cache
            if self.enable_memory_fallback:
                if cache_key in self._memory_cache:
                    self._memory_cache.pop(cache_key, None)
                    self._memory_expiry.pop(cache_key, None)
                    deleted = True
            
            if deleted:
                self.stats.deletes += 1
            
            return deleted
            
        except Exception as e:
            self.stats.errors += 1
            logger.error(f"Cache delete error for key {key}: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        cache_key = self._make_key(key)
        
        try:
            # Check Redis
            if self._redis_available and self._redis:
                exists = await self._redis.exists(cache_key)
                if exists:
                    return True
            
            # Check memory cache
            if self.enable_memory_fallback:
                if cache_key in self._memory_cache:
                    # Check if not expired
                    if cache_key not in self._memory_expiry or self._memory_expiry[cache_key] > datetime.utcnow():
                        return True
                    else:
                        # Clean up expired entry
                        self._memory_cache.pop(cache_key, None)
                        self._memory_expiry.pop(cache_key, None)
            
            return False
            
        except Exception as e:
            self.stats.errors += 1
            logger.error(f"Cache exists error for key {key}: {e}")
            return False
    
    async def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching a pattern."""
        try:
            cleared = 0
            
            # Clear from Redis
            if self._redis_available and self._redis:
                keys = await self._redis.keys(f"{self.key_prefix}{pattern}")
                if keys:
                    cleared += await self._redis.delete(*keys)
            
            # Clear from memory cache
            if self.enable_memory_fallback:
                pattern_key = f"{self.key_prefix}{pattern.replace('*', '')}"
                keys_to_delete = [k for k in self._memory_cache.keys() if k.startswith(pattern_key)]
                for key in keys_to_delete:
                    self._memory_cache.pop(key, None)
                    self._memory_expiry.pop(key, None)
                    cleared += 1
            
            return cleared
            
        except Exception as e:
            self.stats.errors += 1
            logger.error(f"Cache clear pattern error for {pattern}: {e}")
            return 0
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics."""
        redis_info = {}
        if self._redis_available and self._redis:
            try:
                redis_info = await self._redis.info()
            except Exception as e:
                logger.error(f"Failed to get Redis info: {e}")
        
        return {
            "stats": asdict(self.stats),
            "memory_cache_size": len(self._memory_cache),
            "redis_available": self._redis_available,
            "redis_info": redis_info
        }
    
    def cache_result(
        self,
        key_func: Optional[callable] = None,
        ttl: Optional[int] = None
    ):
        """Decorator for caching function results."""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Generate cache key
                if key_func:
                    cache_key = key_func(*args, **kwargs)
                else:
                    # Default key from function name and arguments
                    key_parts = [func.__name__]
                    if args:
                        key_parts.append(self._hash_key(args))
                    if kwargs:
                        key_parts.append(self._hash_key(kwargs))
                    cache_key = ":".join(key_parts)
                
                # Try to get from cache
                cached_result = await self.get(cache_key)
                if cached_result is not None:
                    return cached_result
                
                # Execute function and cache result
                result = await func(*args, **kwargs)
                await self.set(cache_key, result, ttl)
                return result
            
            return wrapper
        return decorator


# Global cache instance
_cache_manager: Optional[CacheManager] = None


def get_cache_manager() -> CacheManager:
    """Get the global cache manager instance."""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager


def init_cache_manager(
    redis_url: Optional[str] = None,
    default_ttl: int = 3600,
    key_prefix: str = "ros:"
) -> CacheManager:
    """Initialize the global cache manager."""
    global _cache_manager
    _cache_manager = CacheManager(
        redis_url=redis_url,
        default_ttl=default_ttl,
        key_prefix=key_prefix
    )
    return _cache_manager