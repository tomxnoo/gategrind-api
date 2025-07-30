#!/usr/bin/env python3
"""
Test Discord.py logging with enhanced formatter.
This simulates the same logging calls that Discord.py makes.
"""

import logging
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

def test_discord_logging():
    """Test the same logging calls that Discord.py makes"""
    print("Testing Discord.py logging simulation...")
    
    # Configure enhanced logging
    try:
        from shared.utils.enhanced_logging import configure_project_logging
        configure_project_logging()
        print("* Enhanced logging configured")
    except ImportError:
        print("* Enhanced logging not available")
        return
    
    # Simulate Discord.py logger calls
    discord_logger = logging.getLogger('discord.ui.view')
    
    print("\nSimulating Discord.py messages:")
    
    # Normal info message
    discord_logger.info("View interaction completed successfully")
    
    # Warning message (like timeout)
    discord_logger.warning("View timeout occurred, cleaning up resources")
    
    # Error message (like the one in your console_log.md)
    discord_logger.error("Ignoring exception in view <SystemHubPublicView timeout=None children=1>")
    discord_logger.error("Traceback (most recent call last):\n  File 'dropdown.py', line 87, in callback\n    await interaction.response.defer(ephemeral=True)")
    discord_logger.error("discord.errors.NotFound: 404 Not Found (error code: 10062): Unknown interaction")
    
    # Test other loggers too
    other_logger = logging.getLogger('features.system.ui.dropdown')
    other_logger.warning("This is a warning from your application code")
    other_logger.error("This is an error from your application code")

if __name__ == "__main__":
    test_discord_logging()