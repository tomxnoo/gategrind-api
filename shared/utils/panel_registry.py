# utils/panel_registry.py

# NOTE: Pycord migration: Pycord is a maintained fork of discord.py with the same API, but should be imported as 'import discord' and 'from discord.ext import commands'.
# For maintainers: If you need to use Pycord-specific features, refer to https://docs.pycord.dev/en/master/
import discord  # Pycord (discord.py compatible)

from typing import Type

# Holds panel classes keyed by their `.key`
_PANEL_REGISTRY: dict[str, Type] = {}


def register(panel_cls: Type):
    """
    Call this at module‐load time in each panel’s UI file
    so the panel shows up in the main dropdown.
    """
    _PANEL_REGISTRY[panel_cls.key] = panel_cls
    return panel_cls  # Ensure the decorator returns the class


def get_registered_panels() -> list[Type]:
    """
    Returns the list of panel classes in a specific order.
    """
    # Define the desired order for your 4 panels
    desired_order = ["profile", "log_reps", "quest_log", "buffs"]

    ordered_panels = []

    # Add panels in the desired order
    for key in desired_order:
        if key in _PANEL_REGISTRY:
            ordered_panels.append(_PANEL_REGISTRY[key])

    # Don't add any remaining panels to keep it clean
    return ordered_panels


def get_panel_by_key(key: str) -> Type | None:
    """
    Lookup a panel class by its .key
    """
    return _PANEL_REGISTRY.get(key)
