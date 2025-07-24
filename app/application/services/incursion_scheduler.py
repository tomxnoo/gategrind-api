"""
IncursionScheduler - Background scheduler for managing incursion lifecycle

This scheduler handles:
- Automatic incursion spawning with cooldowns
- Cleanup of expired incursions
- Periodic health checks
- Configurable spawn rates and cooldowns
"""
import asyncio
import logging
import random
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from app.application.services.incursion_service import IncursionService
from app.infrastructure.database.models.v2.incursions import IncursionType, RewardType


@dataclass
class SpawnCooldownConfig:
    """Configuration for incursion spawn cooldowns."""
    min_cooldown_minutes: int = 30  # Minimum time between spawns
    max_cooldown_minutes: int = 120  # Maximum time between spawns
    type_specific_cooldowns: Dict[IncursionType, int] = None  # Type-specific cooldowns
    max_concurrent_incursions: int = 3  # Maximum active incursions at once
    
    def __post_init__(self):
        """Initialize type-specific cooldowns if not provided."""
        if self.type_specific_cooldowns is None:
            self.type_specific_cooldowns = {
                IncursionType.SURGE: 45,      # Quick, frequent challenges
                IncursionType.CHALLENGE: 90,  # Medium frequency
                IncursionType.ANOMALY: 180    # Rare, special events
            }


@dataclass
class IncursionTemplate:
    """Template for generating incursions."""
    title: str
    description: str
    incursion_type: IncursionType
    target_exercise: str
    target_reps_range: tuple[int, int]  # (min, max)
    reward_type: RewardType
    reward_value_range: tuple[int, int]  # (min, max)
    reward_description: str
    duration_hours: float
    weight: float = 1.0  # Probability weight for selection
    metadata: Optional[Dict[str, Any]] = None


class IncursionScheduler:
    """
    Background scheduler for managing incursion lifecycle.
    
    Implements spawn cooldowns and automatic incursion management
    as specified in the story requirements.
    """
    
    def __init__(
        self, 
        incursion_service: IncursionService,
        cooldown_config: Optional[SpawnCooldownConfig] = None
    ):
        """
        Initialize the scheduler.
        
        Args:
            incursion_service: Service for incursion operations
            cooldown_config: Configuration for spawn cooldowns
        """
        self.incursion_service = incursion_service
        self.cooldown_config = cooldown_config or SpawnCooldownConfig()
        self.logger = logging.getLogger(__name__)
        
        # Tracking state
        self.last_spawn_time: Optional[datetime] = None
        self.last_spawn_by_type: Dict[IncursionType, datetime] = {}
        self.is_running = False
        self.scheduler_task: Optional[asyncio.Task] = None
        
        # Incursion templates for generation
        self.incursion_templates = self._initialize_templates()
    
    def _initialize_templates(self) -> List[IncursionTemplate]:
        """Initialize predefined incursion templates."""
        return [
            # SURGE incursions - Quick, frequent challenges
            IncursionTemplate(
                title="Push-Up Surge",
                description="A sudden surge of energy demands immediate push-ups!",
                incursion_type=IncursionType.SURGE,
                target_exercise="push_ups",
                target_reps_range=(50, 150),
                reward_type=RewardType.XP,
                reward_value_range=(100, 300),
                reward_description="Quick XP boost",
                duration_hours=2.0,
                weight=3.0
            ),
            IncursionTemplate(
                title="Squat Surge",
                description="The ground trembles - squats are needed now!",
                incursion_type=IncursionType.SURGE,
                target_exercise="squats",
                target_reps_range=(75, 200),
                reward_type=RewardType.XP,
                reward_value_range=(120, 350),
                reward_description="Leg strength XP",
                duration_hours=2.5,
                weight=3.0
            ),
            
            # CHALLENGE incursions - Medium difficulty, longer duration
            IncursionTemplate(
                title="The Iron Challenge",
                description="A test of endurance and strength across multiple exercises.",
                incursion_type=IncursionType.CHALLENGE,
                target_exercise="mixed",
                target_reps_range=(300, 500),
                reward_type=RewardType.BUFF,
                reward_value_range=(5, 15),
                reward_description="Strength multiplier buff",
                duration_hours=8.0,
                weight=2.0
            ),
            IncursionTemplate(
                title="Cardio Gauntlet",
                description="High-intensity cardio challenge for the brave.",
                incursion_type=IncursionType.CHALLENGE,
                target_exercise="cardio",
                target_reps_range=(200, 400),
                reward_type=RewardType.XP,
                reward_value_range=(500, 800),
                reward_description="Endurance mastery XP",
                duration_hours=6.0,
                weight=2.0
            ),
            
            # ANOMALY incursions - Rare, special events
            IncursionTemplate(
                title="The Great Convergence",
                description="A rare cosmic event that amplifies all physical training!",
                incursion_type=IncursionType.ANOMALY,
                target_exercise="any",
                target_reps_range=(1000, 2000),
                reward_type=RewardType.ITEM,
                reward_value_range=(1, 3),
                reward_description="Legendary training equipment",
                duration_hours=24.0,
                weight=0.5,
                metadata={"special_event": True, "multiplier": 2.0}
            ),
            IncursionTemplate(
                title="Temporal Rift Training",
                description="Time itself bends to reward dedicated training.",
                incursion_type=IncursionType.ANOMALY,
                target_exercise="any",
                target_reps_range=(500, 1500),
                reward_type=RewardType.BUFF,
                reward_value_range=(20, 50),
                reward_description="Time dilation training buff",
                duration_hours=12.0,
                weight=0.3,
                metadata={"temporal_event": True}
            )
        ]
    
    async def start(self) -> None:
        """Start the background scheduler."""
        if self.is_running:
            self.logger.warning("Scheduler is already running")
            return
        
        self.is_running = True
        self.scheduler_task = asyncio.create_task(self._scheduler_loop())
        self.logger.info("IncursionScheduler started")
    
    async def stop(self) -> None:
        """Stop the background scheduler."""
        if not self.is_running:
            return
        
        self.is_running = False
        if self.scheduler_task:
            self.scheduler_task.cancel()
            try:
                await self.scheduler_task
            except asyncio.CancelledError:
                pass
        
        self.logger.info("IncursionScheduler stopped")
    
    async def _scheduler_loop(self) -> None:
        """Main scheduler loop."""
        self.logger.info("Scheduler loop started")
        
        while self.is_running:
            try:
                # Cleanup expired incursions
                await self._cleanup_expired()
                
                # Check if we should spawn a new incursion
                if await self._should_spawn_incursion():
                    await self._spawn_random_incursion()
                
                # Health check
                await self._perform_health_check()
                
                # Wait before next iteration (check every 5 minutes)
                await asyncio.sleep(300)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in scheduler loop: {e}", exc_info=True)
                # Continue running despite errors
                await asyncio.sleep(60)  # Wait a minute before retrying
    
    async def _cleanup_expired(self) -> None:
        """Clean up expired incursions."""
        try:
            cleaned_count = await self.incursion_service.cleanup_expired_incursions()
            if cleaned_count > 0:
                self.logger.info(f"Cleaned up {cleaned_count} expired incursions")
        except Exception as e:
            self.logger.error(f"Error cleaning up expired incursions: {e}")
    
    async def _should_spawn_incursion(self) -> bool:
        """
        Determine if a new incursion should be spawned based on cooldowns.
        
        Returns:
            bool: True if an incursion should be spawned
        """
        try:
            # Check if we're at max concurrent incursions
            active_incursions = await self.incursion_service.get_active_incursions()
            if len(active_incursions) >= self.cooldown_config.max_concurrent_incursions:
                return False
            
            current_time = datetime.now(timezone.utc)
            
            # Check global cooldown
            if self.last_spawn_time:
                min_cooldown = timedelta(minutes=self.cooldown_config.min_cooldown_minutes)
                if current_time - self.last_spawn_time < min_cooldown:
                    return False
            
            # If no recent spawn, use random cooldown to determine spawn
            if self.last_spawn_time:
                max_cooldown = timedelta(minutes=self.cooldown_config.max_cooldown_minutes)
                time_since_last = current_time - self.last_spawn_time
                
                # Probability increases over time within the cooldown window
                if time_since_last >= max_cooldown:
                    return True  # Definitely spawn if max cooldown reached
                
                # Calculate spawn probability based on time elapsed
                cooldown_progress = time_since_last.total_seconds() / max_cooldown.total_seconds()
                spawn_probability = max(0.1, cooldown_progress * 0.8)  # 10% to 80% chance
                
                return random.random() < spawn_probability
            
            # First spawn - always allow
            return True
            
        except Exception as e:
            self.logger.error(f"Error checking spawn conditions: {e}")
            return False
    
    async def _spawn_random_incursion(self) -> None:
        """Spawn a random incursion based on templates and cooldowns."""
        try:
            # Filter templates based on type-specific cooldowns
            available_templates = []
            current_time = datetime.now(timezone.utc)
            
            for template in self.incursion_templates:
                # Check type-specific cooldown
                if template.incursion_type in self.last_spawn_by_type:
                    last_spawn = self.last_spawn_by_type[template.incursion_type]
                    type_cooldown = self.cooldown_config.type_specific_cooldowns[template.incursion_type]
                    cooldown_delta = timedelta(minutes=type_cooldown)
                    
                    if current_time - last_spawn < cooldown_delta:
                        continue  # Skip this type due to cooldown
                
                available_templates.append(template)
            
            if not available_templates:
                self.logger.debug("No templates available due to cooldowns")
                return
            
            # Select template based on weights
            template = self._weighted_random_choice(available_templates)
            
            # Generate incursion from template
            incursion = await self._create_incursion_from_template(template)
            
            # Update spawn tracking
            self.last_spawn_time = current_time
            self.last_spawn_by_type[template.incursion_type] = current_time
            
            self.logger.info(f"Spawned new incursion: {incursion.title} ({incursion.incursion_type.value})")
            
        except Exception as e:
            self.logger.error(f"Error spawning incursion: {e}", exc_info=True)
    
    def _weighted_random_choice(self, templates: List[IncursionTemplate]) -> IncursionTemplate:
        """Select a template using weighted random selection."""
        total_weight = sum(t.weight for t in templates)
        random_value = random.uniform(0, total_weight)
        
        current_weight = 0
        for template in templates:
            current_weight += template.weight
            if random_value <= current_weight:
                return template
        
        # Fallback to last template
        return templates[-1]
    
    async def _create_incursion_from_template(self, template: IncursionTemplate) -> Any:
        """Create an incursion from a template with randomized values."""
        # Randomize target reps
        target_reps = random.randint(*template.target_reps_range)
        
        # Randomize reward value
        reward_value = random.randint(*template.reward_value_range)
        
        # Create the incursion
        return await self.incursion_service.create_incursion(
            title=template.title,
            description=template.description,
            incursion_type=template.incursion_type,
            target_exercise=template.target_exercise,
            target_reps=target_reps,
            reward_type=template.reward_type,
            reward_value=reward_value,
            reward_description=template.reward_description,
            duration_hours=template.duration_hours,
            metadata=template.metadata
        )
    
    async def _perform_health_check(self) -> None:
        """Perform periodic health checks."""
        try:
            health_result = await self.incursion_service.health_check()
            if health_result.get("status") != "healthy":
                self.logger.warning(f"Incursion service health check failed: {health_result}")
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
    
    async def force_spawn_incursion(self, incursion_type: Optional[IncursionType] = None) -> bool:
        """
        Force spawn an incursion, bypassing cooldowns.
        
        Args:
            incursion_type: Specific type to spawn, or None for random
            
        Returns:
            bool: True if incursion was spawned successfully
        """
        try:
            # Filter templates by type if specified
            if incursion_type:
                available_templates = [t for t in self.incursion_templates if t.incursion_type == incursion_type]
            else:
                available_templates = self.incursion_templates
            
            if not available_templates:
                self.logger.warning(f"No templates available for type {incursion_type}")
                return False
            
            # Select and spawn
            template = self._weighted_random_choice(available_templates)
            incursion = await self._create_incursion_from_template(template)
            
            # Update tracking
            current_time = datetime.now(timezone.utc)
            self.last_spawn_time = current_time
            self.last_spawn_by_type[template.incursion_type] = current_time
            
            self.logger.info(f"Force spawned incursion: {incursion.title}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error force spawning incursion: {e}", exc_info=True)
            return False
    
    def get_cooldown_status(self) -> Dict[str, Any]:
        """
        Get current cooldown status for monitoring.
        
        Returns:
            Dict[str, Any]: Cooldown status information
        """
        current_time = datetime.now(timezone.utc)
        
        status = {
            "is_running": self.is_running,
            "last_spawn_time": self.last_spawn_time.isoformat() if self.last_spawn_time else None,
            "global_cooldown_remaining": None,
            "type_cooldowns": {},
            "config": {
                "min_cooldown_minutes": self.cooldown_config.min_cooldown_minutes,
                "max_cooldown_minutes": self.cooldown_config.max_cooldown_minutes,
                "max_concurrent_incursions": self.cooldown_config.max_concurrent_incursions
            }
        }
        
        # Calculate global cooldown remaining
        if self.last_spawn_time:
            min_cooldown = timedelta(minutes=self.cooldown_config.min_cooldown_minutes)
            time_since_last = current_time - self.last_spawn_time
            if time_since_last < min_cooldown:
                remaining = min_cooldown - time_since_last
                status["global_cooldown_remaining"] = int(remaining.total_seconds())
        
        # Calculate type-specific cooldowns
        for inc_type, last_spawn in self.last_spawn_by_type.items():
            type_cooldown = self.cooldown_config.type_specific_cooldowns[inc_type]
            cooldown_delta = timedelta(minutes=type_cooldown)
            time_since_last = current_time - last_spawn
            
            if time_since_last < cooldown_delta:
                remaining = cooldown_delta - time_since_last
                status["type_cooldowns"][inc_type.value] = {
                    "last_spawn": last_spawn.isoformat(),
                    "cooldown_remaining": int(remaining.total_seconds())
                }
            else:
                status["type_cooldowns"][inc_type.value] = {
                    "last_spawn": last_spawn.isoformat(),
                    "cooldown_remaining": 0
                }
        
        return status