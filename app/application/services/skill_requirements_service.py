"""
Skill Requirements Service for GateGrind V2
==========================================

This service handles dynamic loading, caching, and management of skill tree requirements.
It provides a configurable system for skill node requirements that can be modified
without code changes.
"""

import json
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta

from app.application.game_data.skill_tree_config import SkillNodeRequirements, SKILL_TREE_CONFIG
from core.redis_cache import RedisCache


logger = logging.getLogger(__name__)


@dataclass
class RequirementValidationError:
    """Error details for requirement validation failures"""
    field: str
    value: Any
    message: str


class SkillRequirementsService:
    """Service for managing dynamic skill tree requirements"""
    
    def __init__(self, redis_cache: Optional[RedisCache] = None):
        self.redis_cache = redis_cache
        self.cache_ttl = 3600  # 1 hour cache TTL
        self.config_file_path = Path("app/application/game_data/skill_requirements_config.json")
        self._requirements_cache: Dict[str, SkillNodeRequirements] = {}
        self._last_loaded: Optional[datetime] = None
        
    async def get_node_requirements(self, node_id: str) -> Optional[SkillNodeRequirements]:
        """
        Get requirements for a specific skill node.
        
        Args:
            node_id: The ID of the skill node
            
        Returns:
            SkillNodeRequirements object or None if not found
        """
        try:
            # Try cache first
            if self.redis_cache:
                cached_data = await self.redis_cache.get(f"skill_requirements:{node_id}")
                if cached_data:
                    logger.debug(f"Retrieved requirements for {node_id} from cache")
                    return SkillNodeRequirements(**json.loads(cached_data))
            
            # Load from configuration
            requirements = await self._load_requirements_from_config()
            if node_id in requirements:
                # Cache the result
                if self.redis_cache:
                    await self.redis_cache.set(
                        f"skill_requirements:{node_id}",
                        json.dumps(asdict(requirements[node_id])),
                        ttl=self.cache_ttl
                    )
                return requirements[node_id]
            
            # Fallback to hardcoded config
            return self._get_hardcoded_requirements(node_id)
            
        except Exception as e:
            logger.error(f"Error getting requirements for node {node_id}: {e}")
            # Fallback to hardcoded config
            return self._get_hardcoded_requirements(node_id)
    
    async def update_node_requirements(
        self, 
        node_id: str, 
        requirements: SkillNodeRequirements
    ) -> bool:
        """
        Update requirements for a specific skill node.
        
        Args:
            node_id: The ID of the skill node
            requirements: New requirements for the node
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Validate requirements
            validation_errors = self._validate_requirements(requirements)
            if validation_errors:
                logger.error(f"Validation errors for {node_id}: {validation_errors}")
                return False
            
            # Load current config
            config = await self._load_config_file()
            
            # Update the specific node
            config[node_id] = asdict(requirements)
            
            # Save to file
            await self._save_config_file(config)
            
            # Update cache
            if self.redis_cache:
                await self.redis_cache.set(
                    f"skill_requirements:{node_id}",
                    json.dumps(asdict(requirements)),
                    ttl=self.cache_ttl
                )
                # Invalidate the full requirements cache
                await self.redis_cache.delete("skill_requirements:all")
            
            # Update local cache
            self._requirements_cache[node_id] = requirements
            
            logger.info(f"Successfully updated requirements for node {node_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating requirements for node {node_id}: {e}")
            return False
    
    async def get_all_requirements(self) -> Dict[str, SkillNodeRequirements]:
        """
        Get all skill node requirements.
        
        Returns:
            Dictionary mapping node IDs to their requirements
        """
        try:
            # Try cache first
            if self.redis_cache:
                cached_data = await self.redis_cache.get("skill_requirements:all")
                if cached_data:
                    logger.debug("Retrieved all requirements from cache")
                    data = json.loads(cached_data)
                    return {
                        node_id: SkillNodeRequirements(**req_data)
                        for node_id, req_data in data.items()
                    }
            
            # Load from configuration
            requirements = await self._load_requirements_from_config()
            
            # Cache the result
            if self.redis_cache:
                cache_data = {
                    node_id: asdict(req) for node_id, req in requirements.items()
                }
                await self.redis_cache.set(
                    "skill_requirements:all",
                    json.dumps(cache_data),
                    ttl=self.cache_ttl
                )
            
            return requirements
            
        except Exception as e:
            logger.error(f"Error getting all requirements: {e}")
            # Fallback to hardcoded config
            return self._get_all_hardcoded_requirements()
    
    async def invalidate_cache(self, node_id: Optional[str] = None) -> None:
        """
        Invalidate cached requirements.
        
        Args:
            node_id: Specific node to invalidate, or None for all
        """
        if not self.redis_cache:
            return
            
        try:
            if node_id:
                await self.redis_cache.delete(f"skill_requirements:{node_id}")
                logger.info(f"Invalidated cache for node {node_id}")
            else:
                # Invalidate all requirements cache
                await self.redis_cache.delete("skill_requirements:all")
                # Also invalidate individual node caches
                all_requirements = await self._load_requirements_from_config()
                for node_id in all_requirements.keys():
                    await self.redis_cache.delete(f"skill_requirements:{node_id}")
                logger.info("Invalidated all requirements cache")
                
        except Exception as e:
            logger.error(f"Error invalidating cache: {e}")
    
    def _validate_requirements(self, requirements: SkillNodeRequirements) -> List[RequirementValidationError]:
        """
        Validate skill node requirements.
        
        Args:
            requirements: Requirements to validate
            
        Returns:
            List of validation errors
        """
        errors = []
        
        # Validate stat requirements are non-negative
        if requirements.str_points < 0:
            errors.append(RequirementValidationError("str_points", requirements.str_points, "Must be non-negative"))
        if requirements.end_points < 0:
            errors.append(RequirementValidationError("end_points", requirements.end_points, "Must be non-negative"))
        if requirements.tech_points < 0:
            errors.append(RequirementValidationError("tech_points", requirements.tech_points, "Must be non-negative"))
        
        # Validate skill point requirements are non-negative
        if requirements.skill_points < 0:
            errors.append(RequirementValidationError("skill_points", requirements.skill_points, "Must be non-negative"))
        if requirements.strength_skill_points < 0:
            errors.append(RequirementValidationError("strength_skill_points", requirements.strength_skill_points, "Must be non-negative"))
        if requirements.endurance_skill_points < 0:
            errors.append(RequirementValidationError("endurance_skill_points", requirements.endurance_skill_points, "Must be non-negative"))
        if requirements.technique_skill_points < 0:
            errors.append(RequirementValidationError("technique_skill_points", requirements.technique_skill_points, "Must be non-negative"))
        
        # Validate level requirement
        if requirements.min_ascendant_level < 1:
            errors.append(RequirementValidationError("min_ascendant_level", requirements.min_ascendant_level, "Must be at least 1"))
        
        # Validate aura requirement
        if requirements.min_aura_score < 0:
            errors.append(RequirementValidationError("min_aura_score", requirements.min_aura_score, "Must be non-negative"))
        
        return errors
    
    async def _load_requirements_from_config(self) -> Dict[str, SkillNodeRequirements]:
        """Load requirements from configuration file or fallback to hardcoded"""
        try:
            config = await self._load_config_file()
            requirements = {}
            
            for node_id, req_data in config.items():
                try:
                    requirements[node_id] = SkillNodeRequirements(**req_data)
                except Exception as e:
                    logger.warning(f"Error loading requirements for {node_id}: {e}, using hardcoded fallback")
                    hardcoded = self._get_hardcoded_requirements(node_id)
                    if hardcoded:
                        requirements[node_id] = hardcoded
            
            return requirements
            
        except Exception as e:
            logger.warning(f"Error loading config file: {e}, using hardcoded requirements")
            return self._get_all_hardcoded_requirements()
    
    async def _load_config_file(self) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        try:
            if self.config_file_path.exists():
                with open(self.config_file_path, 'r') as f:
                    return json.load(f)
            else:
                logger.info("Config file doesn't exist, creating from hardcoded requirements")
                # Create initial config from hardcoded requirements
                hardcoded = self._get_all_hardcoded_requirements()
                config = {
                    node_id: asdict(req) for node_id, req in hardcoded.items()
                }
                await self._save_config_file(config)
                return config
                
        except Exception as e:
            logger.error(f"Error loading config file: {e}")
            return {}
    
    async def _save_config_file(self, config: Dict[str, Any]) -> None:
        """Save configuration to JSON file"""
        try:
            # Ensure directory exists
            self.config_file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save with pretty formatting
            with open(self.config_file_path, 'w') as f:
                json.dump(config, f, indent=2, sort_keys=True)
                
            logger.info(f"Saved configuration to {self.config_file_path}")
            
        except Exception as e:
            logger.error(f"Error saving config file: {e}")
            raise
    
    def _get_hardcoded_requirements(self, node_id: str) -> Optional[SkillNodeRequirements]:
        """Get requirements from hardcoded skill tree config"""
        for category_nodes in SKILL_TREE_CONFIG.values():
            for node in category_nodes:
                if node.id == node_id:
                    return node.requirements
        return None
    
    def _get_all_hardcoded_requirements(self) -> Dict[str, SkillNodeRequirements]:
        """Get all requirements from hardcoded skill tree config"""
        requirements = {}
        for category_nodes in SKILL_TREE_CONFIG.values():
            for node in category_nodes:
                requirements[node.id] = node.requirements
        return requirements