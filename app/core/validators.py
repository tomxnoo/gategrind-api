"""
Enhanced validation utilities for the application.

This module provides comprehensive validation patterns including:
- Custom Pydantic validators
- Business rule validation
- Input sanitization
- Type safety helpers
"""
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union, Type, get_type_hints
from pydantic import validator, BaseModel, Field
from pydantic.validators import str_validator
from functools import wraps

from app.core.exceptions import ValidationError


class DiscordUserIdValidator:
    """Validator for Discord user IDs."""
    
    @staticmethod
    def validate_discord_user_id(v: Any) -> str:
        """Validate Discord user ID format."""
        if not v:
            raise ValueError("Discord user ID is required")
        
        # Convert to string if integer
        v_str = str(v)
        
        # Discord user IDs are 17-19 digit numbers
        if not re.match(r'^\d{17,19}$', v_str):
            raise ValueError("Invalid Discord user ID format")
        
        return v_str


class GameValueValidator:
    """Validator for game-specific values."""
    
    @staticmethod
    def validate_level(v: int) -> int:
        """Validate player level."""
        if not isinstance(v, int):
            raise ValueError("Level must be an integer")
        
        if v < 1:
            raise ValueError("Level must be at least 1")
        
        if v > 1000:  # Reasonable upper bound
            raise ValueError("Level cannot exceed 1000")
        
        return v
    
    @staticmethod
    def validate_xp(v: int) -> int:
        """Validate experience points."""
        if not isinstance(v, int):
            raise ValueError("XP must be an integer")
        
        if v < 0:
            raise ValueError("XP cannot be negative")
        
        if v > 1_000_000_000:  # 1 billion max
            raise ValueError("XP value too large")
        
        return v
    
    @staticmethod
    def validate_aura(v: int) -> int:
        """Validate aura value."""
        if not isinstance(v, int):
            raise ValueError("Aura must be an integer")
        
        if v < 0:
            raise ValueError("Aura cannot be negative")
        
        if v > 100_000:  # Reasonable upper bound
            raise ValueError("Aura value too large")
        
        return v
    
    @staticmethod
    def validate_dungeon_level(v: int) -> int:
        """Validate dungeon level."""
        if not isinstance(v, int):
            raise ValueError("Dungeon level must be an integer")
        
        if v < 1:
            raise ValueError("Dungeon level must be at least 1")
        
        if v > 100:  # Current max dungeon level
            raise ValueError("Dungeon level cannot exceed 100")
        
        return v


class StringSanitizer:
    """String sanitization utilities."""
    
    @staticmethod
    def sanitize_user_input(v: str, max_length: int = 1000) -> str:
        """Sanitize user input strings."""
        if not isinstance(v, str):
            v = str(v)
        
        # Strip whitespace
        v = v.strip()
        
        # Check length
        if len(v) > max_length:
            raise ValueError(f"Input too long (max {max_length} characters)")
        
        # Remove null bytes and control characters (except newlines and tabs)
        v = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', v)
        
        return v
    
    @staticmethod
    def sanitize_discord_message(v: str) -> str:
        """Sanitize Discord message content."""
        v = StringSanitizer.sanitize_user_input(v, max_length=2000)
        
        # Remove Discord markdown that could be problematic
        # Keep basic formatting but remove @everyone/@here mentions
        v = re.sub(r'@(everyone|here)', '@\u200b\\1', v)  # Zero-width space
        
        return v


class BusinessRuleValidator:
    """Business rule validation utilities."""
    
    @staticmethod
    def validate_dungeon_entry_requirements(
        player_level: int,
        player_aura: int,
        dungeon_level: int,
        required_aura: int
    ) -> None:
        """Validate if player meets dungeon entry requirements."""
        errors = []
        
        # Check level requirements (must be at least dungeon level)
        if player_level < dungeon_level:
            errors.append(f"Player level {player_level} is below required level {dungeon_level}")
        
        # Check aura requirements
        if player_aura < required_aura:
            errors.append(f"Player aura {player_aura} is below required aura {required_aura}")
        
        if errors:
            raise ValidationError(
                "Dungeon entry requirements not met",
                error_code="DUNGEON_REQUIREMENTS_NOT_MET",
                context={"errors": errors}
            )
    
    @staticmethod
    def validate_skill_unlock_requirements(
        player_stats: Dict[str, int],
        required_stats: Dict[str, int]
    ) -> None:
        """Validate if player meets skill unlock requirements."""
        errors = []
        
        for stat_name, required_value in required_stats.items():
            player_value = player_stats.get(stat_name, 0)
            if player_value < required_value:
                errors.append(
                    f"{stat_name}: {player_value}/{required_value}"
                )
        
        if errors:
            raise ValidationError(
                "Skill unlock requirements not met",
                error_code="SKILL_REQUIREMENTS_NOT_MET",
                context={"missing_requirements": errors}
            )
    
    @staticmethod
    def validate_session_timeout(
        session_created_at: datetime,
        timeout_hours: int = 1
    ) -> None:
        """Validate if session has not timed out."""
        if not session_created_at.tzinfo:
            session_created_at = session_created_at.replace(tzinfo=timezone.utc)
        
        now = datetime.now(timezone.utc)
        elapsed_hours = (now - session_created_at).total_seconds() / 3600
        
        if elapsed_hours > timeout_hours:
            raise ValidationError(
                f"Session expired ({elapsed_hours:.1f}h > {timeout_hours}h)",
                error_code="SESSION_EXPIRED",
                context={
                    "created_at": session_created_at.isoformat(),
                    "elapsed_hours": elapsed_hours,
                    "timeout_hours": timeout_hours
                }
            )


def validate_model_fields(model_class: Type[BaseModel]):
    """Decorator to add comprehensive field validation to Pydantic models."""
    
    def decorator(cls):
        # Get type hints for the model
        type_hints = get_type_hints(cls)
        
        # Add validators based on field types and names
        for field_name, field_type in type_hints.items():
            if hasattr(cls, field_name):
                field_info = getattr(cls, field_name)
                
                # Skip if not a Field
                if not isinstance(field_info, type(Field())):
                    continue
                
                # Add Discord user ID validation
                if 'discord_user_id' in field_name.lower():
                    setattr(cls, f'validate_{field_name}', 
                           validator(field_name, allow_reuse=True)(
                               DiscordUserIdValidator.validate_discord_user_id
                           ))
                
                # Add level validation
                elif 'level' in field_name.lower():
                    setattr(cls, f'validate_{field_name}',
                           validator(field_name, allow_reuse=True)(
                               GameValueValidator.validate_level
                           ))
                
                # Add XP validation
                elif field_name.lower() in ['xp', 'experience']:
                    setattr(cls, f'validate_{field_name}',
                           validator(field_name, allow_reuse=True)(
                               GameValueValidator.validate_xp
                           ))
                
                # Add aura validation
                elif 'aura' in field_name.lower():
                    setattr(cls, f'validate_{field_name}',
                           validator(field_name, allow_reuse=True)(
                               GameValueValidator.validate_aura
                           ))
        
        return cls
    
    return decorator


def validate_request_data(
    data: Dict[str, Any],
    schema: Dict[str, Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Validate request data against a schema.
    
    Args:
        data: The data to validate
        schema: Validation schema with field requirements
        
    Returns:
        Validated and sanitized data
        
    Raises:
        ValidationError: If validation fails
    """
    validated_data = {}
    errors = []
    
    for field_name, field_config in schema.items():
        field_value = data.get(field_name)
        is_required = field_config.get('required', False)
        field_type = field_config.get('type', str)
        min_value = field_config.get('min')
        max_value = field_config.get('max')
        pattern = field_config.get('pattern')
        
        # Check required fields
        if is_required and field_value is None:
            errors.append(f"Field '{field_name}' is required")
            continue
        
        # Skip validation for optional None values
        if field_value is None:
            validated_data[field_name] = None
            continue
        
        # Type validation
        try:
            if field_type == int:
                field_value = int(field_value)
            elif field_type == float:
                field_value = float(field_value)
            elif field_type == str:
                field_value = str(field_value).strip()
            elif field_type == bool:
                field_value = bool(field_value)
        except (ValueError, TypeError):
            errors.append(f"Field '{field_name}' must be of type {field_type.__name__}")
            continue
        
        # Range validation for numbers
        if isinstance(field_value, (int, float)):
            if min_value is not None and field_value < min_value:
                errors.append(f"Field '{field_name}' must be >= {min_value}")
                continue
            if max_value is not None and field_value > max_value:
                errors.append(f"Field '{field_name}' must be <= {max_value}")
                continue
        
        # Pattern validation for strings
        if isinstance(field_value, str) and pattern:
            if not re.match(pattern, field_value):
                errors.append(f"Field '{field_name}' does not match required pattern")
                continue
        
        # String sanitization
        if isinstance(field_value, str):
            try:
                field_value = StringSanitizer.sanitize_user_input(field_value)
            except ValueError as e:
                errors.append(f"Field '{field_name}': {str(e)}")
                continue
        
        validated_data[field_name] = field_value
    
    if errors:
        raise ValidationError(
            "Request validation failed",
            error_code="VALIDATION_FAILED",
            context={"field_errors": errors}
        )
    
    return validated_data


class ValidationMixin:
    """Mixin class to add validation methods to services."""
    
    def validate_discord_user_id(self, user_id: Any) -> str:
        """Validate Discord user ID."""
        return DiscordUserIdValidator.validate_discord_user_id(user_id)
    
    def validate_game_values(self, **kwargs) -> Dict[str, Any]:
        """Validate multiple game values."""
        validated = {}
        
        for key, value in kwargs.items():
            if 'level' in key.lower():
                validated[key] = GameValueValidator.validate_level(value)
            elif key.lower() in ['xp', 'experience']:
                validated[key] = GameValueValidator.validate_xp(value)
            elif 'aura' in key.lower():
                validated[key] = GameValueValidator.validate_aura(value)
            else:
                validated[key] = value
        
        return validated
    
    def sanitize_user_input(self, text: str, max_length: int = 1000) -> str:
        """Sanitize user input."""
        return StringSanitizer.sanitize_user_input(text, max_length)


# Export commonly used validators
__all__ = [
    'DiscordUserIdValidator',
    'GameValueValidator', 
    'StringSanitizer',
    'BusinessRuleValidator',
    'validate_model_fields',
    'validate_request_data',
    'ValidationMixin'
]