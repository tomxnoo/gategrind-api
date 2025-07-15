import logging
from typing import List, Dict, Optional
from features.incursions.logic.incursion_manager import IncursionManager
from features.incursions.models.incursion import IncursionType

logger = logging.getLogger(__name__)

class IncursionRepIntegration:
    """Handles rep logging integration with active incursions"""
    
    def __init__(self, bot):
        self.bot = bot
        self.manager = IncursionManager(bot)
    
    async def process_rep_log(self, user_id: int, exercise: str, reps: int, sets: int = 1) -> Dict:
        """Process a rep log and check for incursion contributions"""
        result = {
            "incursions_contributed": [],
            "incursions_completed": [],
            "bonuses_applied": [],
            "total_bonus_xp": 0
        }
        
        try:
            # Get active incursions
            active_incursions = await self.manager.get_active_incursions()
            
            for incursion in active_incursions:
                contribution_result = await self._check_incursion_contribution(
                    incursion, exercise, reps, sets, user_id
                )
                
                if contribution_result["contributed"]:
                    result["incursions_contributed"].append({
                        "incursion_id": incursion.incursion_id,
                        "title": incursion.title,
                        "reps_contributed": contribution_result["reps_contributed"],
                        "bonus_xp": contribution_result["bonus_xp"]
                    })
                    
                    result["total_bonus_xp"] += contribution_result["bonus_xp"]
                    
                    if contribution_result["completed"]:
                        result["incursions_completed"].append({
                            "incursion_id": incursion.incursion_id,
                            "title": incursion.title,
                            "completion_bonus": contribution_result["completion_bonus"]
                        })
                        result["total_bonus_xp"] += contribution_result["completion_bonus"]
                
                # Check for anomaly effects
                if incursion.incursion_type == IncursionType.ANOMALY:
                    anomaly_result = await self._apply_anomaly_effects(
                        incursion, exercise, reps, sets, user_id
                    )
                    if anomaly_result["bonus_applied"]:
                        result["bonuses_applied"].append(anomaly_result)
                        result["total_bonus_xp"] += anomaly_result["bonus_xp"]
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing rep log for incursions: {e}")
            return result
    
    async def _check_incursion_contribution(self, incursion, exercise: str, reps: int, sets: int, user_id: int) -> Dict:
        """Check if a rep log contributes to an incursion"""
        result = {
            "contributed": False,
            "reps_contributed": 0,
            "bonus_xp": 0,
            "completed": False,
            "completion_bonus": 0
        }
        
        # Check if exercise matches incursion target
        if incursion.target_exercise != "any" and incursion.target_exercise != exercise:
            return result
        
        # Calculate contribution based on incursion type
        if incursion.incursion_type == IncursionType.CHALLENGE:
            # Direct rep contribution
            total_reps = reps * sets
            
            # Apply anomaly modifiers if any
            if "rep_multiplier" in incursion.metadata:
                total_reps = int(total_reps * incursion.metadata["rep_multiplier"])
            
            # Contribute to incursion
            await self.manager.contribute_reps(incursion.incursion_id, total_reps)
            
            result["contributed"] = True
            result["reps_contributed"] = total_reps
            
            # Check if incursion is now completed
            updated_incursion = await self.manager.get_incursion_by_id(incursion.incursion_id)
            if updated_incursion and updated_incursion.is_completed and incursion.is_active:
                await self.manager.complete_incursion(incursion.incursion_id)
                result["completed"] = True
                result["completion_bonus"] = incursion.reward_value
        
        elif incursion.incursion_type == IncursionType.SURGE:
            # Surge incursions provide passive bonuses
            if incursion.reward_type.value == "xp":
                bonus_xp = int((reps * sets) * (incursion.reward_value / 100))  # Percentage bonus
                result["contributed"] = True
                result["bonus_xp"] = bonus_xp
        
        return result
    
    async def _apply_anomaly_effects(self, incursion, exercise: str, reps: int, sets: int, user_id: int) -> Dict:
        """Apply special anomaly effects to rep logging"""
        result = {
            "bonus_applied": False,
            "effect_name": incursion.title,
            "bonus_xp": 0,
            "special_effect": None
        }
        
        metadata = incursion.metadata
        
        # Gravitational Flux: Reps count as 0.5x, XP doubled
        if "rep_multiplier" in metadata and "xp_multiplier" in metadata:
            base_xp = reps * sets * 2  # Base XP calculation
            bonus_xp = int(base_xp * (metadata["xp_multiplier"] - 1))
            result["bonus_applied"] = True
            result["bonus_xp"] = bonus_xp
            result["special_effect"] = f"Gravitational Flux: +{bonus_xp} bonus XP"
        
        # Temporal Acceleration: Speed bonus
        elif "speed_bonus" in metadata:
            # This would require timing data from the UI
            # For now, assume 25% chance of speed bonus
            import random
            if random.random() < 0.25:
                bonus_xp = int((reps * sets) * 2)  # Triple XP = 200% bonus
                result["bonus_applied"] = True
                result["bonus_xp"] = bonus_xp
                result["special_effect"] = f"Temporal Acceleration: Lightning fast! +{bonus_xp} bonus XP"
        
        # Mirror Dimension: Pair requirement
        elif "pair_requirement" in metadata:
            if sets >= 2:  # Assume pairs were performed
                bonus_xp = int((reps * sets) * 0.5)  # 150% total = 50% bonus
                result["bonus_applied"] = True
                result["bonus_xp"] = bonus_xp
                result["special_effect"] = f"Mirror Dimension: Perfect synchronization! +{bonus_xp} bonus XP"
        
        return result
    
    async def get_relevant_incursions_for_exercise(self, exercise: str) -> List[Dict]:
        """Get incursions that are relevant to a specific exercise"""
        active_incursions = await self.manager.get_active_incursions()
        relevant = []
        
        for incursion in active_incursions:
            if incursion.target_exercise == "any" or incursion.target_exercise == exercise:
                relevant.append({
                    "incursion_id": incursion.incursion_id,
                    "title": incursion.title,
                    "type": incursion.incursion_type.value,
                    "progress": incursion.progress_percentage,
                    "time_remaining": incursion.time_remaining,
                    "reward": incursion.reward_description
                })
        
        return relevant