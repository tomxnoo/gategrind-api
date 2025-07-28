"""
Shared UI components for Discord panels.
Provides reusable UI elements to avoid code duplication across panels.
"""

from typing import Optional


def create_progress_bar(current: int, total: int, length: int = 10, 
                       filled_char: str = '█', empty_char: str = '░') -> str:
    """
    Creates a visual ASCII progress bar.
    
    Args:
        current: Current value
        total: Maximum/total value
        length: Length of the progress bar in characters (default: 10)
        filled_char: Character to use for filled portion (default: '█')
        empty_char: Character to use for empty portion (default: '░')
        
    Returns:
        Formatted progress bar string like "[████░░░░░░] 40%"
    """
    if total == 0:
        return f"[{empty_char * length}] 0%"
    
    progress = min(1.0, current / total)
    filled_length = int(length * progress)
    bar = filled_char * filled_length + empty_char * (length - filled_length)
    percentage = int(progress * 100)
    
    return f"[{bar}] {percentage}%"


def create_xp_bar(current_xp: int, next_level_xp: int, length: int = 10) -> str:
    """
    Creates a specialized XP progress bar with MAX indicator.
    
    Args:
        current_xp: Current XP amount
        next_level_xp: XP needed for next level
        length: Length of the progress bar (default: 10)
        
    Returns:
        Formatted XP bar string like "[████░░░░░░] 40%" or "[██████████] MAX"
    """
    if not next_level_xp or next_level_xp == 0:
        return f"[{'█' * length}] MAX"
    
    return create_progress_bar(current_xp, next_level_xp, length)


def create_stat_bar(value: int, max_value: int = 100, length: int = 8) -> str:
    """
    Creates a visual bar for stat displays.
    
    Args:
        value: Current stat value
        max_value: Maximum stat value (default: 100)
        length: Length of the bar (default: 8)
        
    Returns:
        Formatted stat bar string like "[▰▰▰▰▱▱▱▱]"
    """
    if max_value == 0:
        return f"[{'▱' * length}]"
    
    progress = min(1.0, value / max_value)
    filled_length = int(length * progress)
    bar = '▰' * filled_length + '▱' * (length - filled_length)
    
    return f"[{bar}]"


def format_tier_name(tier: str) -> str:
    """
    Format dungeon tier name with ANSI color codes.
    
    Args:
        tier: Tier name (shadow, warrior, ascendant)
        
    Returns:
        ANSI color-formatted tier name
    """
    tier_colors = {
        "shadow": "\x1b[1;30m",     # Dark gray
        "warrior": "\x1b[1;34m",    # Blue
        "ascendant": "\x1b[1;35m"   # Purple
    }
    color = tier_colors.get(tier.lower(), "\x1b[1;37m")
    return f"{color}{tier.title()}\x1b[0m"