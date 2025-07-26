"""
Movement API endpoints for V2.

This module provides REST API endpoints for movement and skill tree operations.
It implements the GET /v2/movements/library endpoint that returns the complete
skill tree library structure.
"""
from fastapi import APIRouter, HTTPException, Depends, status
from typing import Dict, Any, List
import logging
from datetime import datetime, timezone

from app.application.services.movement_service import MovementService
from app.api.v2.schemas.movement_schemas import MovementCategoryResponse


# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/movements", tags=["Movements V2"])


async def get_movement_service() -> MovementService:
    """
    Dependency injection for MovementService.
    
    Returns:
        MovementService: Instance of the movement service
    """
    return MovementService()


@router.get(
    "/library",
    response_model=Dict[str, Any],
    summary="Get complete skill tree library",
    description="Returns the complete skill tree library including all categories, nodes, and movements",
    responses={
        200: {
            "description": "Complete skill tree library",
            "content": {
                "application/json": {
                    "example": {
                        "categories": [
                            {
                                "id": "PULL_VERTICAL",
                                "name": "Vertical Pulling",
                                "primary_stat": "STR",
                                "skill_tree": [
                                    {
                                        "id": 1,
                                        "level": 1,
                                        "name": "Foundation",
                                        "description": "Basic vertical pulling movements",
                                        "requirements": {
                                            "ascendant_level": 1,
                                            "str_points": 0,
                                            "end_points": 0,
                                            "tech_points": 0
                                        },
                                        "movements": [
                                            {
                                                "id": 1,
                                                "name": "Negative Pull-ups",
                                                "xp_per_rep": 1.5,
                                                "stat_reward_type": "STR"
                                            }
                                        ]
                                    }
                                ]
                            }
                        ]
                    }
                }
            }
        },
        500: {"description": "Internal server error"}
    }
)
async def get_skill_tree_library(
    movement_service: MovementService = Depends(get_movement_service)
) -> Dict[str, Any]:
    """
    Get the complete skill tree library.
    
    This endpoint returns the entire skill tree structure including:
    - All movement categories with metadata
    - Complete 5-level skill tree structure for each category  
    - Movement progressions linked to appropriate skill nodes
    - Proper JSON serialization with all required fields
    
    Returns:
        Dict[str, Any]: Complete skill tree library structure
        
    Raises:
        HTTPException: If there's an error fetching the data
    """
    try:
        logger.info("Fetching complete skill tree library")
        
        # Fetch the skill tree library from the service
        library_data = await movement_service.get_skill_tree_library()
        
        logger.info(f"Successfully returned skill tree library with {len(library_data.get('categories', []))} categories")
        
        return library_data
        
    except Exception as e:
        logger.error(f"Error fetching skill tree library: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch skill tree library: {str(e)}"
        )
    finally:
        # Clean up the service session
        await movement_service.close_session()


@router.get(
    "/categories",
    response_model=List[MovementCategoryResponse],
    summary="Get all movement categories",
    description="Returns a list of all movement categories without skill tree details"
)
async def get_movement_categories(
    movement_service: MovementService = Depends(get_movement_service)
) -> List[Dict[str, Any]]:
    """
    Get all movement categories.
    
    Returns a simplified list of movement categories without the detailed
    skill tree structure. Useful for category selection interfaces.
    
    Returns:
        List[Dict[str, Any]]: List of movement categories
        
    Raises:
        HTTPException: If there's an error fetching the data
    """
    try:
        logger.info("Fetching movement categories")
        
        categories = await movement_service.get_movement_categories()
        
        logger.info(f"Successfully returned {len(categories)} movement categories")
        
        return categories
        
    except Exception as e:
        logger.error(f"Error fetching movement categories: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch movement categories: {str(e)}"
        )
    finally:
        await movement_service.close_session()


@router.get(
    "/categories/{category_id}",
    response_model=Dict[str, Any],
    summary="Get specific movement category",
    description="Returns a specific movement category with its complete skill tree"
)
async def get_movement_category(
    category_id: str,
    movement_service: MovementService = Depends(get_movement_service)
) -> Dict[str, Any]:
    """
    Get a specific movement category by ID.
    
    Args:
        category_id: The category identifier (e.g., 'PULL_VERTICAL')
        
    Returns:
        Dict[str, Any]: Category data with skill tree
        
    Raises:
        HTTPException: If category not found or error occurs
    """
    try:
        logger.info(f"Fetching movement category: {category_id}")
        
        category_data = await movement_service.get_movement_category(category_id)
        
        if not category_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Movement category '{category_id}' not found"
            )
        
        logger.info(f"Successfully returned movement category: {category_id}")
        
        return category_data
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Error fetching movement category {category_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch movement category: {str(e)}"
        )
    finally:
        await movement_service.close_session()


@router.get(
    "/health",
    summary="Movement service health check",
    description="Check the health status of the movement service"
)
async def movement_service_health(
    movement_service: MovementService = Depends(get_movement_service)
) -> Dict[str, Any]:
    """
    Perform a health check for the movement service.
    
    Returns:
        Dict[str, Any]: Health check results
    """
    try:
        health_data = await movement_service.health_check()
        health_data["timestamp"] = datetime.now(timezone.utc).isoformat()
        
        # Return appropriate status code based on health status
        if health_data.get("status") == "unhealthy":
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=health_data
            )
        
        return health_data
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Health check failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Health check failed"
        )
    finally:
        await movement_service.close_session()