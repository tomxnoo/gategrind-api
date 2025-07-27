# utils/panel_registry.py

# NOTE: Pycord migration: Pycord is a maintained fork of discord.py with the same API, but should be imported as 'import discord' and 'from discord.ext import commands'.
# For maintainers: If you need to use Pycord-specific features, refer to https://docs.pycord.dev/en/master/
import discord  # Pycord (discord.py compatible)

from typing import Dict, Any, List, Type

# Holds panel classes keyed by their `.key`
_PANEL_REGISTRY: Dict[str, Any] = {}
_PANEL_ORDER: List[str] = []

def register(panel_cls: Type):
    """Register a panel class for use in the system hub."""
    if not hasattr(panel_cls, 'key') or not hasattr(panel_cls, 'label'):
        raise TypeError(f"Panel class {panel_cls.__name__} must have 'key' and 'label' attributes.")
    
    key = panel_cls.key
    if key in _PANEL_REGISTRY:
        # Potentially log a warning here if re-registration is not intended
        pass
    _PANEL_REGISTRY[key] = panel_cls
    return panel_cls

def set_panel_order(order: List[str]):
    """
    Sets the global order for panels.
    """
    global _PANEL_ORDER
    _PANEL_ORDER = order


def get_registered_panels() -> list[Type]:
    """
    Returns the list of panel classes in a specific order.
    """
    # Use the globally set order, or a default if not set.
    order = _PANEL_ORDER or ["profile", "profile_v2", "awakening", "log_reps", "quest_log", "buffs", "incursions"]
    
    ordered_panels = []
    
    # Add panels in the desired order
    for key in order:
        if key in _PANEL_REGISTRY:
            ordered_panels.append(_PANEL_REGISTRY[key])
    
    return ordered_panels


def get_panel_by_key(key: str) -> Type | None:
    """
    Lookup a panel class by its .key
    """
    return _PANEL_REGISTRY.get(key)


def debug_registry():
    """Debug function to see what panels are registered"""
    print(f"[DEBUG] Registered panels: {list(_PANEL_REGISTRY.keys())}")
    for key, panel_cls in _PANEL_REGISTRY.items():
        print(f"[DEBUG] Panel '{key}': {panel_cls.__name__}")
    return _PANEL_REGISTRY
