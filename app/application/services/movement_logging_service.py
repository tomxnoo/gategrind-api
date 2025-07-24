"""
Movement logging service for handling exercise rep logging and XP calculation.

This service manages all business logic related to movement logging including:
- Movement validation and lookup
- XP calculation based on reps and movement data
- Integration with ProgressionService for XP distribution
- Aura recalculation after progression changes
"""
import logging
from typing import Dict, Any, Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.application.services.base_service import BaseService
from app.application.services.progression_service import ProgressionService, ProgressionResult
from app.infrastructure.database.models.v2 import Movement


class MovementLogResult:
    """
    Result object for movement logging operations.
    
    Contains all the information about what happened during a movement log.
    """
    
    def __init__(self):
        self.user_id: Optional[int] = None
        self.movement_id: int = 0
        self.movement_name: str = ""
        self.reps_logged: int = 0
        self.xp_earned: Dict[str, int] = {}
        self.level_ups: List[Dict[str, Any]] = []
        self.aura_update: Dict[str, Any] = {}
        self.session_id: Optional[str] = None
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses."""
        return {
            "movement": {
                "id": self.movement_id,
                "name": self.movement_name
            },
            "reps_logged": self.reps_logged,
            "xp_earned": self.xp_earned,
            "level_ups": self.level_ups,
            "aura_update": self.aura_update,
            "session_id": self.session_id
        }


class MovementLoggingService(BaseService):
    """
    Service for managing movement logging and XP calculation.
    
    This service handles:
    - Movement validation and lookup
    - XP calculation based on movement data and reps
    - Integration with ProgressionService for XP distribution
    - Aura recalculation after XP changes
    """
    
    def __init__(self, session: Optional[AsyncSession] = None):
        """Initialize the movement logging service."""
        super().__init__(session)
        self._progression_service = None
    
    async def get_progression_service(self) -> ProgressionService:
        """Get or create a ProgressionService instance."""
        if self._progression_service is None:
            session = await self.get_session()
            self._progression_service = ProgressionService(session=session)
        return self._progression_service
    
    async def log_movement(self, user_id: int, movement_id: int, reps: int, 
                          session_id: Optional[str] = None) -> MovementLogResult:
        """
        Log movement reps and calculate XP rewards.
        
        Enhanced from V1 with:
        - Better validation
        - Improved XP calculations
        - Real-time Aura updates
        - Performance tracking
        
        Args:
            user_id: The user's database ID (not discord_id)
            movement_id: ID of the movement being logged
            reps: Number of repetitions performed (must be positive)
            session_id: Optional session tracking ID
            
        Returns:
            MovementLogResult: Complete movement logging information
            
        Raises:
            ValueError: If movement_id is invalid or reps is not positive
            Exception: If movement not found or database error occurs
        """
        # Validate inputs
        if reps <= 0:
            raise ValueError(f"Reps must be positive, got: {reps}")
        
        if movement_id <= 0:
            raise ValueError(f"Movement ID must be positive, got: {movement_id}")
        
        result = MovementLogResult()
        result.user_id = user_id
        result.movement_id = movement_id
        result.reps_logged = reps
        result.session_id = session_id
        
        try:
            # Execute all movement logging logic in a single transaction
            async def movement_logging_transaction(session: AsyncSession):
                # Fetch movement data
                movement = await self._get_movement_by_id(session, movement_id)
                if not movement:
                    raise Exception(f"Movement with ID {movement_id} not found")
                
                result.movement_name = movement.name
                
                # Calculate XP based on movement data
                xp_calculations = await self._calculate_movement_xp(movement, reps)
                result.xp_earned = xp_calculations
                
                # Get progression service and apply XP
                progression_service = await self.get_progression_service()
                progression_results = []
                
                # Apply global XP
                if xp_calculations.get('global', 0) > 0:
                    global_result = await progression_service.add_xp(
                        user_id=user_id,
                        amount=xp_calculations['global'],
                        category='global'
                    )
                    progression_results.append(('global', global_result))
                
                # Apply stat-specific XP
                stat_mapping = {
                    'STR': 'strength',
                    'END': 'endurance', 
                    'TECH': 'technique'
                }
                
                stat_category = stat_mapping.get(movement.stat_reward_type)
                if stat_category and xp_calculations.get(stat_category, 0) > 0:
                    stat_result = await progression_service.add_xp(
                        user_id=user_id,
                        amount=xp_calculations[stat_category],
                        category=stat_category
                    )
                    progression_results.append((stat_category, stat_result))
                
                # Process progression results
                await self._process_progression_results(progression_results, result)
                
                return result
            
            return await self.execute_in_transaction(movement_logging_transaction)
            
        except Exception as e:
            self.handle_service_error(e, f"log_movement(user_id={user_id}, movement_id={movement_id}, reps={reps})")
            raise
    
    async def _get_movement_by_id(self, session: AsyncSession, movement_id: int) -> Optional[Movement]:
        """Fetch movement by ID."""
        stmt = select(Movement).where(Movement.id == movement_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def _calculate_movement_xp(self, movement: Movement, reps: int) -> Dict[str, int]:
        """
        Calculate XP earned for a movement.
        
        Args:
            movement: Movement database object
            reps: Number of repetitions
            
        Returns:
            Dict with XP amounts for different categories
        """
        # Calculate base XP from movement data
        base_xp_per_rep = movement.xp_per_rep
        total_base_xp = int(base_xp_per_rep * reps)
        
        # XP distribution logic
        xp_calculations = {
            'global': total_base_xp,  # All movements give global XP
        }
        
        # Add stat-specific XP based on movement type
        stat_mapping = {
            'STR': 'strength',
            'END': 'endurance',
            'TECH': 'technique'
        }
        
        stat_category = stat_mapping.get(movement.stat_reward_type)
        if stat_category:
            # Stat-specific XP is typically 75% of base XP
            stat_xp = int(total_base_xp * 0.75)
            xp_calculations[stat_category] = stat_xp
        
        self.logger.info(f"Calculated XP for movement {movement.name} ({reps} reps): {xp_calculations}")
        
        return xp_calculations
    
    async def _process_progression_results(self, progression_results: List[tuple], 
                                         result: MovementLogResult) -> None:
        """Process progression results and update the movement log result."""
        all_level_changes = {}
        aura_info = None
        
        for category, progression_result in progression_results:
            # Collect level changes
            if progression_result.level_changes:
                all_level_changes.update(progression_result.level_changes)
            
            # Use the last aura update (they should all be the same)
            if progression_result.new_aura != progression_result.previous_aura:
                aura_info = {
                    'previous_aura': progression_result.previous_aura,
                    'new_aura': progression_result.new_aura,
                    'change': progression_result.new_aura - progression_result.previous_aura,
                    'reason': f'{category.title()} progression'
                }
        
        # Format level-ups for API response
        level_ups = []
        for category, changes in all_level_changes.items():
            level_ups.append({
                'type': category,
                'new_level': changes['new'],
                'points_earned': changes.get('gained', 0)
            })
        
        result.level_ups = level_ups
        result.aura_update = aura_info or {}
        
        if level_ups:
            self.logger.info(f"User {result.user_id} achieved level-ups: {level_ups}")
    
    async def get_movement_by_id(self, movement_id: int) -> Optional[Dict[str, Any]]:
        """
        Get movement information by ID.
        
        Args:
            movement_id: ID of the movement
            
        Returns:
            Dict with movement information or None if not found
        """
        try:
            session = await self.get_session()
            movement = await self._get_movement_by_id(session, movement_id)
            
            if not movement:
                return None
            
            return {
                'id': movement.id,
                'name': movement.name,
                'xp_per_rep': movement.xp_per_rep,
                'stat_reward_type': movement.stat_reward_type,
                'node_id': movement.node_id
            }
            
        except Exception as e:
            self.handle_service_error(e, f"get_movement_by_id(movement_id={movement_id})")
            raise
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check for the MovementLoggingService.
        
        Returns:
            Dict[str, Any]: Health check results
        """
        try:
            session = await self.get_session()
            
            # Test basic database connectivity by counting movements
            stmt = select(Movement)
            result = await session.execute(stmt)
            movements = result.scalars().all()
            
            # Test progression service health
            progression_service = await self.get_progression_service()
            progression_health = await progression_service.health_check()
            
            return {
                "service": "MovementLoggingService",
                "status": "healthy",
                "database_connection": "ok",
                "movements_count": len(movements),
                "progression_service_status": progression_health.get("status", "unknown"),
                "timestamp": None  # Will be set by the API layer
            }
            
        except Exception as e:
            self.handle_service_error(e, "health_check")
            return {
                "service": "MovementLoggingService",
                "status": "unhealthy",
                "error": str(e),
                "timestamp": None
            }