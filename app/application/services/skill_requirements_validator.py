"""
Skill Requirements Validator for GateGrind V2
============================================

This module provides comprehensive validation for skill tree requirement configurations.
It ensures that requirement data is properly formatted and contains valid values.
"""

import logging
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum

from app.application.game_data.skill_tree_config import SkillNodeRequirements


logger = logging.getLogger(__name__)


class ValidationSeverity(Enum):
    """Severity levels for validation issues"""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationResult:
    """Result of a validation check"""
    field: str
    severity: ValidationSeverity
    message: str
    value: Any
    suggestion: Optional[str] = None


class SkillRequirementsValidator:
    """Validator for skill node requirements configuration"""
    
    def __init__(self):
        self.max_stat_points = 1000  # Maximum reasonable stat points
        self.max_skill_points = 500  # Maximum reasonable skill points
        self.max_ascendant_level = 100  # Maximum ascendant level
        self.max_aura_score = 10000  # Maximum aura score
        self.max_list_length = 50  # Maximum items in requirement lists
    
    def validate_requirements(self, requirements: SkillNodeRequirements) -> List[ValidationResult]:
        """
        Validate a SkillNodeRequirements object.
        
        Args:
            requirements: The requirements to validate
            
        Returns:
            List of validation results
        """
        results = []
        
        # Validate stat requirements
        results.extend(self._validate_stat_requirements(requirements))
        
        # Validate skill point requirements
        results.extend(self._validate_skill_point_requirements(requirements))
        
        # Validate level requirements
        results.extend(self._validate_level_requirements(requirements))
        
        # Validate aura requirements
        results.extend(self._validate_aura_requirements(requirements))
        
        # Validate prerequisite nodes
        results.extend(self._validate_prerequisite_nodes(requirements))
        
        # Validate quest requirements
        results.extend(self._validate_quest_requirements(requirements))
        
        # Validate achievement requirements
        results.extend(self._validate_achievement_requirements(requirements))
        
        # Validate logical consistency
        results.extend(self._validate_logical_consistency(requirements))
        
        return results
    
    def validate_config_format(self, config_data: Dict[str, Any]) -> List[ValidationResult]:
        """
        Validate the format of a requirements configuration.
        
        Args:
            config_data: Raw configuration data to validate
            
        Returns:
            List of validation results
        """
        results = []
        
        if not isinstance(config_data, dict):
            results.append(ValidationResult(
                field="root",
                severity=ValidationSeverity.ERROR,
                message="Configuration must be a dictionary",
                value=type(config_data).__name__,
                suggestion="Ensure the configuration is a JSON object"
            ))
            return results
        
        for node_id, node_config in config_data.items():
            results.extend(self._validate_node_config_format(node_id, node_config))
        
        return results
    
    def validate_node_config_format(self, node_id: str, node_config: Any) -> List[ValidationResult]:
        """
        Validate the format of a single node's configuration.
        
        Args:
            node_id: ID of the skill node
            node_config: Configuration data for the node
            
        Returns:
            List of validation results
        """
        return self._validate_node_config_format(node_id, node_config)
    
    def _validate_stat_requirements(self, requirements: SkillNodeRequirements) -> List[ValidationResult]:
        """Validate stat point requirements"""
        results = []
        
        # Validate str_points
        if requirements.str_points < 0:
            results.append(ValidationResult(
                field="str_points",
                severity=ValidationSeverity.ERROR,
                message="Strength points cannot be negative",
                value=requirements.str_points,
                suggestion="Set to 0 or a positive value"
            ))
        elif requirements.str_points > self.max_stat_points:
            results.append(ValidationResult(
                field="str_points",
                severity=ValidationSeverity.WARNING,
                message=f"Strength points seem unusually high (>{self.max_stat_points})",
                value=requirements.str_points,
                suggestion="Consider if this value is intentional"
            ))
        
        # Validate end_points
        if requirements.end_points < 0:
            results.append(ValidationResult(
                field="end_points",
                severity=ValidationSeverity.ERROR,
                message="Endurance points cannot be negative",
                value=requirements.end_points,
                suggestion="Set to 0 or a positive value"
            ))
        elif requirements.end_points > self.max_stat_points:
            results.append(ValidationResult(
                field="end_points",
                severity=ValidationSeverity.WARNING,
                message=f"Endurance points seem unusually high (>{self.max_stat_points})",
                value=requirements.end_points,
                suggestion="Consider if this value is intentional"
            ))
        
        # Validate tech_points
        if requirements.tech_points < 0:
            results.append(ValidationResult(
                field="tech_points",
                severity=ValidationSeverity.ERROR,
                message="Technique points cannot be negative",
                value=requirements.tech_points,
                suggestion="Set to 0 or a positive value"
            ))
        elif requirements.tech_points > self.max_stat_points:
            results.append(ValidationResult(
                field="tech_points",
                severity=ValidationSeverity.WARNING,
                message=f"Technique points seem unusually high (>{self.max_stat_points})",
                value=requirements.tech_points,
                suggestion="Consider if this value is intentional"
            ))
        
        return results
    
    def _validate_skill_point_requirements(self, requirements: SkillNodeRequirements) -> List[ValidationResult]:
        """Validate skill point requirements"""
        results = []
        
        # Custom field name mapping for thematic consistency
        field_display_names = {
            "skill_points": "Shadow Essence",
            "strength_skill_points": "Strength Skill Points",
            "endurance_skill_points": "Endurance Skill Points",
            "technique_skill_points": "Technique Skill Points"
        }
        
        skill_point_fields = [
            ("skill_points", requirements.skill_points),
            ("strength_skill_points", requirements.strength_skill_points),
            ("endurance_skill_points", requirements.endurance_skill_points),
            ("technique_skill_points", requirements.technique_skill_points)
        ]
        
        for field_name, value in skill_point_fields:
            display_name = field_display_names.get(field_name, field_name.replace('_', ' ').title())
            
            if value < 0:
                results.append(ValidationResult(
                    field=field_name,
                    severity=ValidationSeverity.ERROR,
                    message=f"{display_name} cannot be negative",
                    value=value,
                    suggestion="Set to 0 or a positive value"
                ))
            elif value > self.max_skill_points:
                results.append(ValidationResult(
                    field=field_name,
                    severity=ValidationSeverity.WARNING,
                    message=f"{display_name} seem unusually high (>{self.max_skill_points})",
                    value=value,
                    suggestion="Consider if this value is intentional"
                ))
        
        return results
    
    def _validate_level_requirements(self, requirements: SkillNodeRequirements) -> List[ValidationResult]:
        """Validate level requirements"""
        results = []
        
        if requirements.min_ascendant_level < 1:
            results.append(ValidationResult(
                field="min_ascendant_level",
                severity=ValidationSeverity.ERROR,
                message="Minimum ascendant level must be at least 1",
                value=requirements.min_ascendant_level,
                suggestion="Set to 1 or higher"
            ))
        elif requirements.min_ascendant_level > self.max_ascendant_level:
            results.append(ValidationResult(
                field="min_ascendant_level",
                severity=ValidationSeverity.WARNING,
                message=f"Minimum ascendant level seems unusually high (>{self.max_ascendant_level})",
                value=requirements.min_ascendant_level,
                suggestion="Consider if this value is intentional"
            ))
        
        return results
    
    def _validate_aura_requirements(self, requirements: SkillNodeRequirements) -> List[ValidationResult]:
        """Validate aura requirements"""
        results = []
        
        if requirements.min_aura_score < 0:
            results.append(ValidationResult(
                field="min_aura_score",
                severity=ValidationSeverity.ERROR,
                message="Minimum aura score cannot be negative",
                value=requirements.min_aura_score,
                suggestion="Set to 0 or a positive value"
            ))
        elif requirements.min_aura_score > self.max_aura_score:
            results.append(ValidationResult(
                field="min_aura_score",
                severity=ValidationSeverity.WARNING,
                message=f"Minimum aura score seems unusually high (>{self.max_aura_score})",
                value=requirements.min_aura_score,
                suggestion="Consider if this value is intentional"
            ))
        
        return results
    
    def _validate_prerequisite_nodes(self, requirements: SkillNodeRequirements) -> List[ValidationResult]:
        """Validate prerequisite node requirements"""
        results = []
        
        if not isinstance(requirements.prerequisite_nodes, list):
            results.append(ValidationResult(
                field="prerequisite_nodes",
                severity=ValidationSeverity.ERROR,
                message="Prerequisite nodes must be a list",
                value=type(requirements.prerequisite_nodes).__name__,
                suggestion="Use a list of node IDs"
            ))
            return results
        
        if len(requirements.prerequisite_nodes) > self.max_list_length:
            results.append(ValidationResult(
                field="prerequisite_nodes",
                severity=ValidationSeverity.WARNING,
                message=f"Too many prerequisite nodes (>{self.max_list_length})",
                value=len(requirements.prerequisite_nodes),
                suggestion="Consider reducing the number of prerequisites"
            ))
        
        for i, node_id in enumerate(requirements.prerequisite_nodes):
            if not isinstance(node_id, str):
                results.append(ValidationResult(
                    field=f"prerequisite_nodes[{i}]",
                    severity=ValidationSeverity.ERROR,
                    message="Prerequisite node ID must be a string",
                    value=type(node_id).__name__,
                    suggestion="Use string node IDs"
                ))
            elif not node_id.strip():
                results.append(ValidationResult(
                    field=f"prerequisite_nodes[{i}]",
                    severity=ValidationSeverity.ERROR,
                    message="Prerequisite node ID cannot be empty",
                    value=node_id,
                    suggestion="Provide a valid node ID"
                ))
        
        return results
    
    def _validate_quest_requirements(self, requirements: SkillNodeRequirements) -> List[ValidationResult]:
        """Validate quest requirements"""
        results = []
        
        if not isinstance(requirements.required_quests, list):
            results.append(ValidationResult(
                field="required_quests",
                severity=ValidationSeverity.ERROR,
                message="Required quests must be a list",
                value=type(requirements.required_quests).__name__,
                suggestion="Use a list of quest IDs"
            ))
            return results
        
        if len(requirements.required_quests) > self.max_list_length:
            results.append(ValidationResult(
                field="required_quests",
                severity=ValidationSeverity.WARNING,
                message=f"Too many required quests (>{self.max_list_length})",
                value=len(requirements.required_quests),
                suggestion="Consider reducing the number of required quests"
            ))
        
        for i, quest_id in enumerate(requirements.required_quests):
            if not isinstance(quest_id, str):
                results.append(ValidationResult(
                    field=f"required_quests[{i}]",
                    severity=ValidationSeverity.ERROR,
                    message="Quest ID must be a string",
                    value=type(quest_id).__name__,
                    suggestion="Use string quest IDs"
                ))
            elif not quest_id.strip():
                results.append(ValidationResult(
                    field=f"required_quests[{i}]",
                    severity=ValidationSeverity.ERROR,
                    message="Quest ID cannot be empty",
                    value=quest_id,
                    suggestion="Provide a valid quest ID"
                ))
        
        return results
    
    def _validate_achievement_requirements(self, requirements: SkillNodeRequirements) -> List[ValidationResult]:
        """Validate achievement requirements"""
        results = []
        
        if not isinstance(requirements.required_achievements, list):
            results.append(ValidationResult(
                field="required_achievements",
                severity=ValidationSeverity.ERROR,
                message="Required achievements must be a list",
                value=type(requirements.required_achievements).__name__,
                suggestion="Use a list of achievement IDs"
            ))
            return results
        
        if len(requirements.required_achievements) > self.max_list_length:
            results.append(ValidationResult(
                field="required_achievements",
                severity=ValidationSeverity.WARNING,
                message=f"Too many required achievements (>{self.max_list_length})",
                value=len(requirements.required_achievements),
                suggestion="Consider reducing the number of required achievements"
            ))
        
        for i, achievement_id in enumerate(requirements.required_achievements):
            if not isinstance(achievement_id, str):
                results.append(ValidationResult(
                    field=f"required_achievements[{i}]",
                    severity=ValidationSeverity.ERROR,
                    message="Achievement ID must be a string",
                    value=type(achievement_id).__name__,
                    suggestion="Use string achievement IDs"
                ))
            elif not achievement_id.strip():
                results.append(ValidationResult(
                    field=f"required_achievements[{i}]",
                    severity=ValidationSeverity.ERROR,
                    message="Achievement ID cannot be empty",
                    value=achievement_id,
                    suggestion="Provide a valid achievement ID"
                ))
        
        return results
    
    def _validate_logical_consistency(self, requirements: SkillNodeRequirements) -> List[ValidationResult]:
        """Validate logical consistency of requirements"""
        results = []
        
        # Check if total skill points exceed general skill points
        total_specific_skill_points = (
            requirements.strength_skill_points +
            requirements.endurance_skill_points +
            requirements.technique_skill_points
        )
        
        if total_specific_skill_points > requirements.skill_points and requirements.skill_points > 0:
            results.append(ValidationResult(
                field="skill_points",
                severity=ValidationSeverity.WARNING,
                message="Specific skill points exceed general skill points requirement",
                value=f"General: {requirements.skill_points}, Specific total: {total_specific_skill_points}",
                suggestion="Ensure skill point requirements are logically consistent"
            ))
        
        # Check if stat requirements are balanced
        total_stat_points = requirements.str_points + requirements.end_points + requirements.tech_points
        if total_stat_points > 0:
            max_stat = max(requirements.str_points, requirements.end_points, requirements.tech_points)
            if max_stat > total_stat_points * 0.8:  # One stat is more than 80% of total
                results.append(ValidationResult(
                    field="stat_balance",
                    severity=ValidationSeverity.INFO,
                    message="Requirements heavily favor one stat",
                    value=f"STR: {requirements.str_points}, END: {requirements.end_points}, TECH: {requirements.tech_points}",
                    suggestion="Consider if this stat distribution is intentional"
                ))
        
        return results
    
    def _validate_node_config_format(self, node_id: str, node_config: Any) -> List[ValidationResult]:
        """Validate the format of a single node configuration"""
        results = []
        
        if not isinstance(node_config, dict):
            results.append(ValidationResult(
                field=f"{node_id}",
                severity=ValidationSeverity.ERROR,
                message="Node configuration must be a dictionary",
                value=type(node_config).__name__,
                suggestion="Ensure each node configuration is a JSON object"
            ))
            return results
        
        # Required fields for SkillNodeRequirements
        required_fields = {
            "str_points": int,
            "end_points": int,
            "tech_points": int,
            "skill_points": int,
            "strength_skill_points": int,
            "endurance_skill_points": int,
            "technique_skill_points": int,
            "min_ascendant_level": int,
            "min_aura_score": int,
            "prerequisite_nodes": list,
            "required_quests": list,
            "required_achievements": list
        }
        
        # Check for required fields and types
        for field_name, expected_type in required_fields.items():
            if field_name not in node_config:
                results.append(ValidationResult(
                    field=f"{node_id}.{field_name}",
                    severity=ValidationSeverity.ERROR,
                    message=f"Missing required field '{field_name}'",
                    value=None,
                    suggestion=f"Add '{field_name}' field with {expected_type.__name__} value"
                ))
            else:
                value = node_config[field_name]
                if not isinstance(value, expected_type):
                    results.append(ValidationResult(
                        field=f"{node_id}.{field_name}",
                        severity=ValidationSeverity.ERROR,
                        message=f"Field '{field_name}' must be of type {expected_type.__name__}",
                        value=type(value).__name__,
                        suggestion=f"Change to {expected_type.__name__} value"
                    ))
        
        # Check for unknown fields
        for field_name in node_config.keys():
            if field_name not in required_fields:
                results.append(ValidationResult(
                    field=f"{node_id}.{field_name}",
                    severity=ValidationSeverity.WARNING,
                    message=f"Unknown field '{field_name}'",
                    value=node_config[field_name],
                    suggestion="Remove unknown field or check spelling"
                ))
        
        return results