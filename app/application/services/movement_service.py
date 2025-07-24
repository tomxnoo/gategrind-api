"""
Movement service for handling movement and skill tree operations.

This service manages all business logic related to movements, skill trees,
and movement categories. It provides methods to fetch the complete skill tree
library and handles the complex relationships between categories, nodes, and movements.
"""
from typing import List, Dict, Any, Optional
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.base_service import BaseService
from app.infrastructure.database.models.v2 import MovementCategory, SkillTreeNode, Movement


class MovementService(BaseService):
    """
    Service for managing movements and skill tree operations.
    
    This service handles:
    - Fetching the complete skill tree library
    - Managing movement categories and their relationships
    - Providing structured data for API responses
    """
    
    async def get_skill_tree_library(self) -> Dict[str, Any]:
        """
        Fetch the complete skill tree library with all categories, nodes, and movements.
        
        This method returns the entire skill tree structure including:
        - All movement categories with metadata
        - Complete 5-level skill tree structure for each category
        - Movement progressions linked to appropriate skill nodes
        
        Returns:
            Dict[str, Any]: Complete skill tree library structure
            
        Raises:
            Exception: If there's an error fetching the data
        """
        try:
            session = await self.get_session()
            
            # Fetch all categories with their related skill tree nodes and movements
            # Using selectinload to eagerly load relationships and avoid N+1 queries
            stmt = (
                select(MovementCategory)
                .options(
                    selectinload(MovementCategory.skill_tree_nodes)
                    .selectinload(SkillTreeNode.movements)
                )
                .order_by(MovementCategory.id)
            )
            
            result = await session.execute(stmt)
            categories = result.scalars().all()
            
            # Transform the data into the expected API response format
            library_data = {
                "categories": []
            }
            
            for category in categories:
                category_data = {
                    "id": category.id,
                    "name": category.name,
                    "primary_stat": category.primary_stat,
                    "skill_tree": []
                }
                
                # Sort nodes by level to ensure proper progression order
                sorted_nodes = sorted(category.skill_tree_nodes, key=lambda x: x.level)
                
                for node in sorted_nodes:
                    node_data = {
                        "id": node.id,
                        "level": node.level,
                        "name": node.name,
                        "description": node.description,
                        "requirements": {
                            "ascendant_level": node.required_ascendant_level,
                            "str_points": node.required_str_points,
                            "end_points": node.required_end_points,
                            "tech_points": node.required_tech_points
                        },
                        "movements": []
                    }
                    
                    # Add movements for this node
                    for movement in node.movements:
                        movement_data = {
                            "id": movement.id,
                            "name": movement.name,
                            "xp_per_rep": movement.xp_per_rep,
                            "stat_reward_type": movement.stat_reward_type
                        }
                        node_data["movements"].append(movement_data)
                    
                    category_data["skill_tree"].append(node_data)
                
                library_data["categories"].append(category_data)
            
            self.logger.info(f"Successfully fetched skill tree library with {len(categories)} categories")
            return library_data
            
        except Exception as e:
            self.handle_service_error(e, "get_skill_tree_library")
            raise
    
    async def get_movement_category(self, category_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch a specific movement category by ID.
        
        Args:
            category_id: The category identifier (e.g., 'PULL_VERTICAL')
            
        Returns:
            Optional[Dict[str, Any]]: Category data or None if not found
        """
        try:
            session = await self.get_session()
            
            stmt = (
                select(MovementCategory)
                .options(
                    selectinload(MovementCategory.skill_tree_nodes)
                    .selectinload(SkillTreeNode.movements)
                )
                .where(MovementCategory.id == category_id)
            )
            
            result = await session.execute(stmt)
            category = result.scalar_one_or_none()
            
            if not category:
                return None
            
            # Transform to API format
            category_data = {
                "id": category.id,
                "name": category.name,
                "primary_stat": category.primary_stat,
                "skill_tree": []
            }
            
            sorted_nodes = sorted(category.skill_tree_nodes, key=lambda x: x.level)
            
            for node in sorted_nodes:
                node_data = {
                    "id": node.id,
                    "level": node.level,
                    "name": node.name,
                    "description": node.description,
                    "requirements": {
                        "ascendant_level": node.required_ascendant_level,
                        "str_points": node.required_str_points,
                        "end_points": node.required_end_points,
                        "tech_points": node.required_tech_points
                    },
                    "movements": [
                        {
                            "id": movement.id,
                            "name": movement.name,
                            "xp_per_rep": movement.xp_per_rep,
                            "stat_reward_type": movement.stat_reward_type
                        }
                        for movement in node.movements
                    ]
                }
                category_data["skill_tree"].append(node_data)
            
            return category_data
            
        except Exception as e:
            self.handle_service_error(e, f"get_movement_category({category_id})")
            raise
    
    async def get_movement_categories(self) -> List[Dict[str, Any]]:
        """
        Fetch all movement categories without their skill tree details.
        
        Returns:
            List[Dict[str, Any]]: List of movement categories
        """
        try:
            session = await self.get_session()
            
            stmt = select(MovementCategory).order_by(MovementCategory.id)
            result = await session.execute(stmt)
            categories = result.scalars().all()
            
            return [
                {
                    "id": category.id,
                    "name": category.name,
                    "primary_stat": category.primary_stat
                }
                for category in categories
            ]
            
        except Exception as e:
            self.handle_service_error(e, "get_movement_categories")
            raise
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check for the MovementService.
        
        Returns:
            Dict[str, Any]: Health check results
        """
        try:
            session = await self.get_session()
            
            # Test basic database connectivity by counting categories
            stmt = select(MovementCategory)
            result = await session.execute(stmt)
            categories = result.scalars().all()
            
            return {
                "service": "MovementService",
                "status": "healthy",
                "database_connection": "ok",
                "categories_count": len(categories),
                "timestamp": None  # Will be set by the API layer
            }
            
        except Exception as e:
            self.handle_service_error(e, "health_check")
            return {
                "service": "MovementService",
                "status": "unhealthy",
                "error": str(e),
                "timestamp": None
            }