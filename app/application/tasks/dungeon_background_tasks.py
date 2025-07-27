"""
Background tasks for dungeon system performance optimization.
Handles session cleanup, daily modifier generation, and reward processing.
"""

import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional

from app.application.services.dungeon_service import DungeonService
from app.application.services.dungeon_cache_service import DungeonCacheService
from app.infrastructure.database.models.v2.daily_modifiers import DailyModifier
from app.infrastructure.database.session import get_async_session


logger = logging.getLogger(__name__)


class DungeonBackgroundTasks:
    """Background task manager for dungeon system optimization."""
    
    def __init__(self):
        self.dungeon_service = None
        self.cache_service = None
        self.is_running = False
        
    async def get_dungeon_service(self) -> DungeonService:
        """Get or create dungeon service instance."""
        if self.dungeon_service is None:
            self.dungeon_service = DungeonService()
        return self.dungeon_service
    
    async def get_cache_service(self) -> DungeonCacheService:
        """Get or create cache service instance."""
        if self.cache_service is None:
            self.cache_service = DungeonCacheService()
        return self.cache_service
    
    async def start_background_tasks(self):
        """Start all background tasks."""
        if self.is_running:
            logger.warning("Background tasks already running")
            return
            
        self.is_running = True
        logger.info("Starting dungeon background tasks")
        
        # Start tasks concurrently
        tasks = [
            asyncio.create_task(self._session_cleanup_task()),
            asyncio.create_task(self._daily_modifier_task()),
            asyncio.create_task(self._cache_warmup_task()),
            asyncio.create_task(self._reward_processing_task())
        ]
        
        try:
            await asyncio.gather(*tasks)
        except Exception as e:
            logger.error(f"Background tasks error: {e}")
            self.is_running = False
            raise
    
    async def stop_background_tasks(self):
        """Stop all background tasks."""
        self.is_running = False
        logger.info("Stopping dungeon background tasks")
    
    async def _session_cleanup_task(self):
        """Periodic session cleanup task."""
        while self.is_running:
            try:
                dungeon_service = await self.get_dungeon_service()
                cleanup_stats = await dungeon_service.cleanup_expired_sessions()
                
                if cleanup_stats.get('cleaned_sessions', 0) > 0:
                    logger.info(f"Session cleanup completed: {cleanup_stats}")
                
                # Run every 30 minutes
                await asyncio.sleep(1800)
                
            except Exception as e:
                logger.error(f"Session cleanup task error: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes on error
    
    async def _daily_modifier_task(self):
        """Daily modifier generation and activation task."""
        while self.is_running:
            try:
                await self._check_and_generate_daily_modifier()
                
                # Check every hour
                await asyncio.sleep(3600)
                
            except Exception as e:
                logger.error(f"Daily modifier task error: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes on error
    
    async def _cache_warmup_task(self):
        """Cache warmup and refresh task."""
        while self.is_running:
            try:
                cache_service = await self.get_cache_service()
                
                # Warm up common caches
                await self._warmup_common_caches(cache_service)
                
                # Refresh every 15 minutes
                await asyncio.sleep(900)
                
            except Exception as e:
                logger.error(f"Cache warmup task error: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes on error
    
    async def _reward_processing_task(self):
        """Background reward processing task."""
        while self.is_running:
            try:
                await self._process_pending_rewards()
                
                # Process every 5 minutes
                await asyncio.sleep(300)
                
            except Exception as e:
                logger.error(f"Reward processing task error: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes on error
    
    async def _check_and_generate_daily_modifier(self):
        """Check if new daily modifier is needed and generate it."""
        try:
            async with get_async_session() as session:
                # Check if current modifier is still valid
                from sqlalchemy import select
                result = await session.execute(
                    select(DailyModifier).where(
                        DailyModifier.is_active == True
                    )
                )
                current_modifier = result.scalar_one_or_none()
                
                now = datetime.now(timezone.utc)
                
                # Generate new modifier if none exists or current one expired
                if not current_modifier or (current_modifier.expires_at and current_modifier.expires_at <= now):
                    await self._generate_new_daily_modifier(session)
                    
                    # Invalidate cache
                    cache_service = await self.get_cache_service()
                    await cache_service.invalidate_daily_modifier_cache()
                
        except Exception as e:
            logger.error(f"Daily modifier check error: {e}")
            raise
    
    async def _generate_new_daily_modifier(self, session):
        """Generate a new daily modifier."""
        try:
            # Deactivate current modifier
            from sqlalchemy import update
            await session.execute(
                update(DailyModifier)
                .where(DailyModifier.is_active == True)
                .values(is_active=False)
            )
            
            # Create new modifier
            import random
            modifier_types = ['experience_boost', 'shadow_key_discount', 'trial_reduction', 'reward_multiplier']
            modifier_type = random.choice(modifier_types)
            
            # Calculate modifier values based on type
            modifier_values = self._calculate_modifier_values(modifier_type)
            
            new_modifier = DailyModifier(
                modifier_type=modifier_type,
                modifier_value=modifier_values['value'],
                description=modifier_values['description'],
                is_active=True,
                created_at=datetime.now(timezone.utc),
                expires_at=datetime.now(timezone.utc) + timedelta(hours=24)
            )
            
            session.add(new_modifier)
            await session.commit()
            
            logger.info(f"Generated new daily modifier: {modifier_type}")
            
        except Exception as e:
            await session.rollback()
            logger.error(f"Failed to generate daily modifier: {e}")
            raise
    
    def _calculate_modifier_values(self, modifier_type: str) -> Dict[str, Any]:
        """Calculate values for different modifier types."""
        import random
        
        if modifier_type == 'experience_boost':
            value = random.uniform(1.2, 1.5)  # 20-50% boost
            description = f"Experience boost: +{int((value - 1) * 100)}%"
        elif modifier_type == 'shadow_key_discount':
            value = random.uniform(0.5, 0.8)  # 20-50% discount
            description = f"Shadow Key discount: -{int((1 - value) * 100)}%"
        elif modifier_type == 'trial_reduction':
            value = random.randint(1, 2)  # 1-2 fewer trials
            description = f"Trial reduction: -{value} trial(s)"
        elif modifier_type == 'reward_multiplier':
            value = random.uniform(1.1, 1.3)  # 10-30% more rewards
            description = f"Reward multiplier: +{int((value - 1) * 100)}%"
        else:
            value = 1.0
            description = "No modifier"
        
        return {'value': value, 'description': description}
    
    async def _warmup_common_caches(self, cache_service: DungeonCacheService):
        """Warm up commonly used caches."""
        try:
            # Warm up daily modifier cache
            await cache_service.get_cached_daily_modifier()
            
            # Warm up common dungeon level requirements (levels 1-10)
            for level in range(1, 11):
                await cache_service.get_cached_level_requirements(level)
            
            logger.debug("Cache warmup completed")
            
        except Exception as e:
            logger.error(f"Cache warmup error: {e}")
    
    async def _process_pending_rewards(self):
        """Process any pending reward distributions."""
        try:
            # This would integrate with the reward system
            # For now, just log that we're checking
            logger.debug("Checking for pending rewards to process")
            
            # Future implementation would:
            # 1. Query for completed sessions with unprocessed rewards
            # 2. Calculate and distribute rewards
            # 3. Update session status
            
        except Exception as e:
            logger.error(f"Reward processing error: {e}")


# Global instance for background tasks
dungeon_background_tasks = DungeonBackgroundTasks()


async def start_dungeon_background_tasks():
    """Start dungeon background tasks."""
    await dungeon_background_tasks.start_background_tasks()


async def stop_dungeon_background_tasks():
    """Stop dungeon background tasks."""
    await dungeon_background_tasks.stop_background_tasks()