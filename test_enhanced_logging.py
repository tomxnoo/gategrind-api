#!/usr/bin/env python3
"""
Test script to demonstrate the enhanced logging improvements.
Shows the difference between old wall-of-text logging and new structured format.
"""

import logging
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

def test_basic_logging():
    """Test basic Python logging (old way)"""
    print("\n" + "="*80)
    print("BASIC LOGGING (Old way - hard to read)")
    print("="*80)
    
    # Configure basic logging like before
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        force=True  # Reset any existing configuration
    )
    
    logger = logging.getLogger('demo_basic')
    
    logger.debug("This is a debug message that gets lost in the wall of text")
    logger.info("This is an info message that blends in with everything else")
    logger.warning("This is a warning message that should stand out but doesn't")
    logger.error("This is an error message that's hard to spot")
    logger.critical("This is a critical message that gets buried")
    
    # Simulate a typical Discord.py error like in your console_log.md
    logger.error("discord.errors.NotFound: 404 Not Found (error code: 10062): Unknown interaction")
    logger.error("Traceback (most recent call last):\n  File 'dropdown.py', line 87, in callback\n    await interaction.response.defer(ephemeral=True)")


def test_enhanced_logging():
    """Test enhanced logging (new way)"""
    print("\n" + "="*80)
    print("ENHANCED LOGGING (New way - easy to read)")
    print("="*80)
    
    try:
        from shared.utils.enhanced_logging import EnhancedLogger
        
        # Configure enhanced logging
        EnhancedLogger.setup_enhanced_logging(
            level='DEBUG',
            use_colors=True,
            compact=False
        )
        
        logger = logging.getLogger('demo_enhanced')
        
        logger.debug("This is a debug message with clear visual separation")
        logger.info("This is an info message with success indicator")
        logger.warning("This is a warning message that stands out clearly")
        logger.error("This is an error message that's impossible to miss")
        logger.critical("This is a critical message with maximum visibility")
        
        # Simulate the same Discord.py error but now much more visible
        logger.error("discord.errors.NotFound: 404 Not Found (error code: 10062): Unknown interaction")
        logger.error("Traceback (most recent call last):\n  File 'dropdown.py', line 87, in callback\n    await interaction.response.defer(ephemeral=True)")
        
    except ImportError as e:
        print(f"Enhanced logging not available: {e}")


def main():
    print("Console Logging Improvement Demonstration")
    print("This shows how WARN and ERROR messages now stand out from the wall of text")
    
    # Test basic logging first
    test_basic_logging()
    
    # Test enhanced logging
    test_enhanced_logging()
    
    print("\n" + "="*80)
    print("SUMMARY:")
    print("* Errors now have visual separators and bold text")
    print("* Warnings have clear highlighting")
    print("* Colors help distinguish log levels")
    print("* Visual symbols ([ERROR], [WARN], [INFO]) provide instant recognition")
    print("* No more hunting through walls of text for important messages!")
    print("="*80)


if __name__ == "__main__":
    main()