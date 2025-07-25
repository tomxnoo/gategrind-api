"""
Admin API for Skill Requirements Management - GateGrind V2
========================================================

This module provides admin API endpoints for managing skill tree requirements.
It allows administrators to view, update, and validate skill node requirements
through a RESTful interface.
"""

import logging
from typing import Dict, List, Optional
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from app.application.game_data.skill_tree_config import SkillNodeRequirements
from app.application.services.skill_requirements_service import SkillRequirementsService
from app.application.services.skill_requirements_validator import (
    SkillRequirementsValidator, 
    ValidationResult, 
    ValidationSeverity
)
from core.redis_cache import RedisCache


logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(
    prefix="/admin/skill-requirements",
    tags=["Admin - Skill Requirements"]
)


# Pydantic models for API
class SkillNodeRequirementsRequest(BaseModel):
    """Request model for updating skill node requirements"""
    str_points: int = Field(ge=0, description="Required strength points")
    end_points: int = Field(ge=0, description="Required endurance points")
    tech_points: int = Field(ge=0, description="Required technique points")
    skill_points: int = Field(ge=0, description="Required Shadow Essence (universal mystical currency)")
    strength_skill_points: int = Field(ge=0, description="Required strength skill points")
    endurance_skill_points: int = Field(ge=0, description="Required endurance skill points")
    technique_skill_points: int = Field(ge=0, description="Required technique skill points")
    min_ascendant_level: int = Field(ge=1, description="Minimum ascendant level")
    min_aura_score: int = Field(ge=0, description="Minimum aura score")
    prerequisite_nodes: List[str] = Field(default_factory=list, description="Required prerequisite node IDs")
    required_quests: List[str] = Field(default_factory=list, description="Required quest IDs")
    required_achievements: List[str] = Field(default_factory=list, description="Required achievement IDs")


class SkillNodeRequirementsResponse(BaseModel):
    """Response model for skill node requirements"""
    node_id: str
    requirements: SkillNodeRequirementsRequest


class ValidationResultResponse(BaseModel):
    """Response model for validation results"""
    field: str
    severity: str
    message: str
    value: str
    suggestion: Optional[str] = None


class BulkUpdateRequest(BaseModel):
    """Request model for bulk updating multiple node requirements"""
    updates: Dict[str, SkillNodeRequirementsRequest]


class BulkUpdateResponse(BaseModel):
    """Response model for bulk update results"""
    successful_updates: List[str]
    failed_updates: Dict[str, str]
    validation_warnings: Dict[str, List[ValidationResultResponse]]


# Dependency injection
async def get_requirements_service() -> SkillRequirementsService:
    """Get skill requirements service instance"""
    # In development mode, we don't use Redis
    return SkillRequirementsService(redis_cache=None)


async def get_validator() -> SkillRequirementsValidator:
    """Get skill requirements validator instance"""
    return SkillRequirementsValidator()


# API Endpoints
@router.get(
    "/nodes/{node_id}",
    response_model=SkillNodeRequirementsResponse,
    summary="Get skill node requirements",
    description="Retrieve the current requirements for a specific skill node"
)
async def get_node_requirements(
    node_id: str,
    service: SkillRequirementsService = Depends(get_requirements_service)
):
    """Get requirements for a specific skill node"""
    try:
        requirements = await service.get_node_requirements(node_id)
        if not requirements:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Skill node '{node_id}' not found"
            )
        
        return SkillNodeRequirementsResponse(
            node_id=node_id,
            requirements=SkillNodeRequirementsRequest(
                str_points=requirements.str_points,
                end_points=requirements.end_points,
                tech_points=requirements.tech_points,
                skill_points=requirements.skill_points,
                strength_skill_points=requirements.strength_skill_points,
                endurance_skill_points=requirements.endurance_skill_points,
                technique_skill_points=requirements.technique_skill_points,
                min_ascendant_level=requirements.min_ascendant_level,
                min_aura_score=requirements.min_aura_score,
                prerequisite_nodes=requirements.prerequisite_nodes,
                required_quests=requirements.required_quests,
                required_achievements=requirements.required_achievements
            )
        )
        
    except Exception as e:
        logger.error(f"Error getting requirements for node {node_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.put(
    "/nodes/{node_id}",
    response_model=SkillNodeRequirementsResponse,
    summary="Update skill node requirements",
    description="Update the requirements for a specific skill node"
)
async def update_node_requirements(
    node_id: str,
    requirements_request: SkillNodeRequirementsRequest,
    service: SkillRequirementsService = Depends(get_requirements_service),
    validator: SkillRequirementsValidator = Depends(get_validator)
):
    """Update requirements for a specific skill node"""
    try:
        # Convert request to SkillNodeRequirements
        requirements = SkillNodeRequirements(
            str_points=requirements_request.str_points,
            end_points=requirements_request.end_points,
            tech_points=requirements_request.tech_points,
            skill_points=requirements_request.skill_points,
            strength_skill_points=requirements_request.strength_skill_points,
            endurance_skill_points=requirements_request.endurance_skill_points,
            technique_skill_points=requirements_request.technique_skill_points,
            min_ascendant_level=requirements_request.min_ascendant_level,
            min_aura_score=requirements_request.min_aura_score,
            prerequisite_nodes=requirements_request.prerequisite_nodes,
            required_quests=requirements_request.required_quests,
            required_achievements=requirements_request.required_achievements
        )
        
        # Validate requirements
        validation_results = validator.validate_requirements(requirements)
        errors = [r for r in validation_results if r.severity == ValidationSeverity.ERROR]
        
        if errors:
            error_messages = [f"{r.field}: {r.message}" for r in errors]
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Validation errors: {'; '.join(error_messages)}"
            )
        
        # Update requirements
        success = await service.update_node_requirements(node_id, requirements)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update requirements"
            )
        
        # Return updated requirements
        return SkillNodeRequirementsResponse(
            node_id=node_id,
            requirements=requirements_request
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating requirements for node {node_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get(
    "/nodes",
    response_model=List[SkillNodeRequirementsResponse],
    summary="Get all skill node requirements",
    description="Retrieve requirements for all skill nodes"
)
async def get_all_node_requirements(
    service: SkillRequirementsService = Depends(get_requirements_service)
):
    """Get requirements for all skill nodes"""
    try:
        all_requirements = await service.get_all_requirements()
        
        return [
            SkillNodeRequirementsResponse(
                node_id=node_id,
                requirements=SkillNodeRequirementsRequest(
                    str_points=req.str_points,
                    end_points=req.end_points,
                    tech_points=req.tech_points,
                    skill_points=req.skill_points,
                    strength_skill_points=req.strength_skill_points,
                    endurance_skill_points=req.endurance_skill_points,
                    technique_skill_points=req.technique_skill_points,
                    min_ascendant_level=req.min_ascendant_level,
                    min_aura_score=req.min_aura_score,
                    prerequisite_nodes=req.prerequisite_nodes,
                    required_quests=req.required_quests,
                    required_achievements=req.required_achievements
                )
            )
            for node_id, req in all_requirements.items()
        ]
        
    except Exception as e:
        logger.error(f"Error getting all requirements: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post(
    "/validate/{node_id}",
    response_model=List[ValidationResultResponse],
    summary="Validate skill node requirements",
    description="Validate requirements for a specific skill node without updating"
)
async def validate_node_requirements(
    node_id: str,
    requirements_request: SkillNodeRequirementsRequest,
    validator: SkillRequirementsValidator = Depends(get_validator)
):
    """Validate requirements for a specific skill node"""
    try:
        # Convert request to SkillNodeRequirements
        requirements = SkillNodeRequirements(
            str_points=requirements_request.str_points,
            end_points=requirements_request.end_points,
            tech_points=requirements_request.tech_points,
            skill_points=requirements_request.skill_points,
            strength_skill_points=requirements_request.strength_skill_points,
            endurance_skill_points=requirements_request.endurance_skill_points,
            technique_skill_points=requirements_request.technique_skill_points,
            min_ascendant_level=requirements_request.min_ascendant_level,
            min_aura_score=requirements_request.min_aura_score,
            prerequisite_nodes=requirements_request.prerequisite_nodes,
            required_quests=requirements_request.required_quests,
            required_achievements=requirements_request.required_achievements
        )
        
        # Validate requirements
        validation_results = validator.validate_requirements(requirements)
        
        return [
            ValidationResultResponse(
                field=result.field,
                severity=result.severity.value,
                message=result.message,
                value=str(result.value),
                suggestion=result.suggestion
            )
            for result in validation_results
        ]
        
    except Exception as e:
        logger.error(f"Error validating requirements for node {node_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post(
    "/bulk-update",
    response_model=BulkUpdateResponse,
    summary="Bulk update skill node requirements",
    description="Update requirements for multiple skill nodes in a single request"
)
async def bulk_update_requirements(
    bulk_request: BulkUpdateRequest,
    service: SkillRequirementsService = Depends(get_requirements_service),
    validator: SkillRequirementsValidator = Depends(get_validator)
):
    """Bulk update requirements for multiple skill nodes"""
    try:
        successful_updates = []
        failed_updates = {}
        validation_warnings = {}
        
        for node_id, requirements_request in bulk_request.updates.items():
            try:
                # Convert request to SkillNodeRequirements
                requirements = SkillNodeRequirements(
                    str_points=requirements_request.str_points,
                    end_points=requirements_request.end_points,
                    tech_points=requirements_request.tech_points,
                    skill_points=requirements_request.skill_points,
                    strength_skill_points=requirements_request.strength_skill_points,
                    endurance_skill_points=requirements_request.endurance_skill_points,
                    technique_skill_points=requirements_request.technique_skill_points,
                    min_ascendant_level=requirements_request.min_ascendant_level,
                    min_aura_score=requirements_request.min_aura_score,
                    prerequisite_nodes=requirements_request.prerequisite_nodes,
                    required_quests=requirements_request.required_quests,
                    required_achievements=requirements_request.required_achievements
                )
                
                # Validate requirements
                validation_results = validator.validate_requirements(requirements)
                errors = [r for r in validation_results if r.severity == ValidationSeverity.ERROR]
                warnings = [r for r in validation_results if r.severity == ValidationSeverity.WARNING]
                
                if errors:
                    error_messages = [f"{r.field}: {r.message}" for r in errors]
                    failed_updates[node_id] = f"Validation errors: {'; '.join(error_messages)}"
                    continue
                
                if warnings:
                    validation_warnings[node_id] = [
                        ValidationResultResponse(
                            field=w.field,
                            severity=w.severity.value,
                            message=w.message,
                            value=str(w.value),
                            suggestion=w.suggestion
                        )
                        for w in warnings
                    ]
                
                # Update requirements
                success = await service.update_node_requirements(node_id, requirements)
                if success:
                    successful_updates.append(node_id)
                else:
                    failed_updates[node_id] = "Failed to update requirements"
                    
            except Exception as e:
                failed_updates[node_id] = f"Error: {str(e)}"
        
        return BulkUpdateResponse(
            successful_updates=successful_updates,
            failed_updates=failed_updates,
            validation_warnings=validation_warnings
        )
        
    except Exception as e:
        logger.error(f"Error in bulk update: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.delete(
    "/cache",
    summary="Clear requirements cache",
    description="Clear the cached skill requirements data"
)
async def clear_requirements_cache(
    node_id: Optional[str] = None,
    service: SkillRequirementsService = Depends(get_requirements_service)
):
    """Clear requirements cache"""
    try:
        await service.invalidate_cache(node_id)
        
        if node_id:
            message = f"Cache cleared for node '{node_id}'"
        else:
            message = "All requirements cache cleared"
            
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": message}
        )
        
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )