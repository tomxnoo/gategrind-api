# Caching & Observability

## Overview

The GateGrind V2 backend implements comprehensive caching and observability strategies to ensure optimal performance, reliability, and maintainability. This document outlines the Redis caching implementation and Sentry-based observability approach.

## Redis Caching Strategy

### Cache Architecture

The caching layer uses Redis as a high-performance, in-memory data store to reduce database load and improve response times for frequently accessed data.

#### Cache Configuration
```python
# app/infrastructure/cache/cache_service.py
from redis import Redis
from app.core.config import settings

class CacheService:
    def __init__(self):
        self.redis = Redis.from_url(
            settings.redis_url,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True
        )
    
    async def get(self, key: str) -> Optional[str]:
        """Get value from cache"""
        return await self.redis.get(key)
    
    async def set(self, key: str, value: str, ttl: int = None) -> bool:
        """Set value in cache with optional TTL"""
        return await self.redis.set(
            key, 
            value, 
            ex=ttl or settings.redis_ttl_default
        )
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        return await self.redis.delete(key)
    
    async def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate all keys matching pattern"""
        keys = await self.redis.keys(pattern)
        if keys:
            return await self.redis.delete(*keys)
        return 0
```

### Cache Key Strategy

#### Hierarchical Key Structure
```python
# app/infrastructure/cache/cache_keys.py
class CacheKeys:
    # User-related caches
    USER_PROFILE = "user:profile:{user_id}"
    USER_STATS = "user:stats:{user_id}"
    USER_AURA = "user:aura:{user_id}"
    USER_SKILL_PROGRESS = "user:skills:{user_id}"
    
    # Skill tree caches
    SKILL_TREE_STRUCTURE = "skill_tree:structure"
    SKILL_NODE = "skill_tree:node:{node_id}"
    SKILL_PREREQUISITES = "skill_tree:prereqs:{node_id}"
    
    # Quest and dungeon caches
    ACTIVE_QUESTS = "user:quests:active:{user_id}"
    QUEST_TEMPLATE = "quest:template:{quest_id}"
    DUNGEON_PROGRESS = "user:dungeon:{user_id}:{dungeon_id}"
    
    # Movement and logging caches
    MOVEMENT_CATEGORIES = "movements:categories"
    RECENT_MOVEMENTS = "user:movements:recent:{user_id}"
    
    # System-wide caches
    DAILY_LOGIN_REWARDS = "system:daily_rewards"
    AWAKENING_QUESTS = "system:awakening_quests:{date}"
    
    @staticmethod
    def user_pattern(user_id: str) -> str:
        """Get pattern to match all user-related keys"""
        return f"user:*:{user_id}*"
    
    @staticmethod
    def skill_tree_pattern() -> str:
        """Get pattern to match all skill tree keys"""
        return "skill_tree:*"
```

### Caching Patterns

#### 1. Cache-Aside Pattern
```python
# app/application/services/progression_service.py
class ProgressionService:
    def __init__(self, cache: CacheService, user_repo: UserRepository):
        self.cache = cache
        self.user_repo = user_repo
    
    async def get_user_aura(self, user_id: str) -> float:
        # Try cache first
        cache_key = CacheKeys.USER_AURA.format(user_id=user_id)
        cached_aura = await self.cache.get(cache_key)
        
        if cached_aura is not None:
            return float(cached_aura)
        
        # Calculate from database
        aura = await self._calculate_aura(user_id)
        
        # Cache the result
        await self.cache.set(cache_key, str(aura), ttl=300)  # 5 minutes
        
        return aura
```

#### 2. Write-Through Pattern
```python
async def update_user_stats(self, user_id: str, stat_updates: Dict[str, int]):
    # Update database
    await self.user_repo.update_stats(user_id, stat_updates)
    
    # Update cache
    cache_key = CacheKeys.USER_STATS.format(user_id=user_id)
    updated_stats = await self.user_repo.get_user_stats(user_id)
    await self.cache.set(cache_key, json.dumps(updated_stats), ttl=600)
    
    # Invalidate dependent caches
    await self.cache.delete(CacheKeys.USER_AURA.format(user_id=user_id))
    await self.cache.delete(CacheKeys.USER_PROFILE.format(user_id=user_id))
```

#### 3. Cache Invalidation Strategy
```python
class CacheInvalidationService:
    def __init__(self, cache: CacheService):
        self.cache = cache
    
    async def invalidate_user_caches(self, user_id: str):
        """Invalidate all caches for a specific user"""
        pattern = CacheKeys.user_pattern(user_id)
        await self.cache.invalidate_pattern(pattern)
    
    async def invalidate_skill_tree_caches(self):
        """Invalidate skill tree caches when structure changes"""
        pattern = CacheKeys.skill_tree_pattern()
        await self.cache.invalidate_pattern(pattern)
    
    async def invalidate_on_movement_log(self, user_id: str):
        """Invalidate relevant caches when movement is logged"""
        keys_to_invalidate = [
            CacheKeys.USER_STATS.format(user_id=user_id),
            CacheKeys.USER_AURA.format(user_id=user_id),
            CacheKeys.RECENT_MOVEMENTS.format(user_id=user_id),
            CacheKeys.USER_SKILL_PROGRESS.format(user_id=user_id)
        ]
        
        for key in keys_to_invalidate:
            await self.cache.delete(key)
```

### Cache TTL Strategy

#### TTL Configuration by Data Type
```python
class CacheTTL:
    # User data - moderate TTL, frequently updated
    USER_PROFILE = 600      # 10 minutes
    USER_STATS = 300        # 5 minutes
    USER_AURA = 300         # 5 minutes
    
    # Skill tree - long TTL, rarely changes
    SKILL_TREE_STRUCTURE = 3600    # 1 hour
    SKILL_NODE = 1800              # 30 minutes
    
    # Quest data - short TTL, dynamic content
    ACTIVE_QUESTS = 180     # 3 minutes
    QUEST_TEMPLATE = 900    # 15 minutes
    
    # Movement data - very short TTL, real-time updates
    RECENT_MOVEMENTS = 120  # 2 minutes
    
    # System data - long TTL, stable content
    MOVEMENT_CATEGORIES = 7200     # 2 hours
    DAILY_LOGIN_REWARDS = 86400    # 24 hours
```

## Sentry Observability

### Error Tracking & Performance Monitoring

#### Sentry Configuration
```python
# app/core/logging.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.redis import RedisIntegration

def setup_sentry():
    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        environment=settings.environment,
        traces_sample_rate=0.1,  # 10% of transactions
        profiles_sample_rate=0.1,  # 10% of transactions
        integrations=[
            FastApiIntegration(auto_enabling_integrations=False),
            SqlalchemyIntegration(),
            RedisIntegration(),
        ],
        before_send=filter_sensitive_data,
        before_send_transaction=filter_sensitive_transactions,
    )

def filter_sensitive_data(event, hint):
    """Filter out sensitive information from error reports"""
    if 'request' in event:
        # Remove sensitive headers
        if 'headers' in event['request']:
            sensitive_headers = ['authorization', 'cookie', 'x-api-key']
            for header in sensitive_headers:
                event['request']['headers'].pop(header, None)
    
    return event
```

#### Custom Error Context
```python
# app/core/exceptions.py
from sentry_sdk import set_tag, set_context, capture_exception

class GateGrindException(Exception):
    """Base exception for GateGrind application"""
    
    def __init__(self, message: str, user_id: str = None, context: dict = None):
        super().__init__(message)
        self.user_id = user_id
        self.context = context or {}
        
        # Add context to Sentry
        if user_id:
            set_tag("user_id", user_id)
        
        if context:
            set_context("error_context", context)

class ProgressionCalculationError(GateGrindException):
    """Raised when progression calculations fail"""
    pass

class QuestGenerationError(GateGrindException):
    """Raised when quest generation fails"""
    pass

class DungeonAccessError(GateGrindException):
    """Raised when dungeon access is denied"""
    pass
```

#### Performance Monitoring
```python
# app/infrastructure/monitoring/metrics.py
from sentry_sdk import start_transaction, start_span
import time
from functools import wraps

def monitor_performance(operation_name: str):
    """Decorator to monitor function performance"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            with start_transaction(op="function", name=operation_name):
                start_time = time.time()
                
                try:
                    result = await func(*args, **kwargs)
                    
                    # Record success metrics
                    duration = time.time() - start_time
                    set_tag("operation_status", "success")
                    set_context("performance", {
                        "duration_ms": duration * 1000,
                        "function": func.__name__
                    })
                    
                    return result
                    
                except Exception as e:
                    # Record error metrics
                    duration = time.time() - start_time
                    set_tag("operation_status", "error")
                    set_context("performance", {
                        "duration_ms": duration * 1000,
                        "function": func.__name__,
                        "error_type": type(e).__name__
                    })
                    
                    capture_exception(e)
                    raise
                    
        return wrapper
    return decorator

# Usage example
@monitor_performance("aura_calculation")
async def calculate_user_aura(user_id: str) -> float:
    # Aura calculation logic
    pass
```

### Database Query Monitoring

#### Slow Query Detection
```python
# app/infrastructure/db/database.py
from sqlalchemy import event
from sqlalchemy.engine import Engine
import time
import logging

logger = logging.getLogger(__name__)

@event.listens_for(Engine, "before_cursor_execute")
def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    context._query_start_time = time.time()

@event.listens_for(Engine, "after_cursor_execute")
def receive_after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    total = time.time() - context._query_start_time
    
    # Log slow queries
    if total > 0.5:  # 500ms threshold
        logger.warning(
            f"Slow query detected: {total:.2f}s",
            extra={
                "query": statement[:200],  # First 200 chars
                "duration": total,
                "parameters": str(parameters)[:100] if parameters else None
            }
        )
        
        # Send to Sentry for slow queries
        with start_span(op="db.query", description="slow_query"):
            set_context("slow_query", {
                "statement": statement[:500],
                "duration": total,
                "threshold_exceeded": True
            })
```

### Health Checks & Monitoring

#### Application Health Endpoints
```python
# app/infrastructure/monitoring/health_checks.py
from fastapi import APIRouter, HTTPException
from app.infrastructure.db.database import get_db
from app.infrastructure.cache.cache_service import CacheService

router = APIRouter()

@router.get("/health")
async def health_check():
    """Basic health check endpoint"""
    return {"status": "healthy", "timestamp": time.time()}

@router.get("/health/detailed")
async def detailed_health_check(
    db: Session = Depends(get_db),
    cache: CacheService = Depends(get_cache_service)
):
    """Detailed health check with dependency verification"""
    health_status = {
        "status": "healthy",
        "timestamp": time.time(),
        "checks": {}
    }
    
    # Database health
    try:
        db.execute("SELECT 1")
        health_status["checks"]["database"] = "healthy"
    except Exception as e:
        health_status["checks"]["database"] = "unhealthy"
        health_status["status"] = "degraded"
        capture_exception(e)
    
    # Redis health
    try:
        await cache.redis.ping()
        health_status["checks"]["redis"] = "healthy"
    except Exception as e:
        health_status["checks"]["redis"] = "unhealthy"
        health_status["status"] = "degraded"
        capture_exception(e)
    
    # External API health (if applicable)
    try:
        # Check Discord API connectivity
        health_status["checks"]["discord_api"] = "healthy"
    except Exception as e:
        health_status["checks"]["discord_api"] = "unhealthy"
        health_status["status"] = "degraded"
        capture_exception(e)
    
    if health_status["status"] != "healthy":
        raise HTTPException(status_code=503, detail=health_status)
    
    return health_status
```

### Logging Strategy

#### Structured Logging Configuration
```python
# app/core/logging.py
import logging
import json
from datetime import datetime

class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured JSON logging"""
    
    def format(self, record):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add extra fields if present
        if hasattr(record, 'user_id'):
            log_entry["user_id"] = record.user_id
        
        if hasattr(record, 'request_id'):
            log_entry["request_id"] = record.request_id
        
        if hasattr(record, 'duration'):
            log_entry["duration_ms"] = record.duration
        
        return json.dumps(log_entry)

def setup_logging():
    """Configure application logging"""
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format='%(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('app.log') if settings.environment != 'production' else logging.NullHandler()
        ]
    )
    
    # Set structured formatter for production
    if settings.environment == 'production':
        for handler in logging.root.handlers:
            handler.setFormatter(StructuredFormatter())
```

### Monitoring Dashboards

#### Key Metrics to Track
1. **Application Performance**
   - Request latency (p50, p95, p99)
   - Request rate (requests per second)
   - Error rate (4xx, 5xx responses)

2. **Database Performance**
   - Query execution time
   - Connection pool usage
   - Slow query frequency

3. **Cache Performance**
   - Cache hit/miss ratio
   - Cache response time
   - Memory usage

4. **Business Metrics**
   - User progression events
   - Quest completion rates
   - Dungeon success rates
   - Daily active users

#### Alert Configuration
```python
# Example alert thresholds
ALERT_THRESHOLDS = {
    "error_rate": 0.05,        # 5% error rate
    "response_time_p95": 2.0,  # 2 seconds
    "cache_hit_ratio": 0.8,    # 80% cache hit ratio
    "db_connection_usage": 0.9, # 90% connection pool usage
    "memory_usage": 0.85,      # 85% memory usage
}
```

---
*This caching and observability strategy ensures the GateGrind V2 backend maintains high performance, reliability, and provides comprehensive insights into system behavior and user interactions.*