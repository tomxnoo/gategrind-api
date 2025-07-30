#!/usr/bin/env python3
"""
Terminal color test - Check if your terminal supports colors
"""

import os
import sys
import logging

def test_terminal_colors():
    """Test if terminal supports colors and enhanced logging"""
    print("=== TERMINAL COLOR DIAGNOSTICS ===")
    
    # Check environment variables
    print(f"Platform: {sys.platform}")
    print(f"Terminal program: {os.environ.get('TERM_PROGRAM', 'unknown')}")
    print(f"WT_SESSION: {'WT_SESSION' in os.environ}")
    print(f"ANSICON: {'ANSICON' in os.environ}")
    print(f"COLORTERM: {'COLORTERM' in os.environ}")
    print(f"Is TTY: {hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()}")
    
    # Test ANSI colors directly
    print("\n=== DIRECT ANSI COLOR TEST ===")
    print("\033[31mThis should be RED\033[0m")
    print("\033[33mThis should be YELLOW\033[0m")  
    print("\033[32mThis should be GREEN\033[0m")
    print("\033[36mThis should be CYAN\033[0m")
    print("\033[35mThis should be MAGENTA\033[0m")
    
    # Test enhanced logging
    print("\n=== ENHANCED LOGGING TEST ===")
    sys.path.insert(0, os.path.dirname(__file__))
    
    try:
        from shared.utils.enhanced_logging import configure_project_logging, ColoredFormatter
        
        # Check if colors will be enabled
        formatter = ColoredFormatter()
        print(f"Enhanced logging colors enabled: {formatter.use_colors}")
        
        configure_project_logging()
        
        logger = logging.getLogger('color_test')
        logger.info("INFO message - should be green")
        logger.warning("WARNING message - should have yellow separators")
        logger.error("ERROR message - should have red separators")
        
    except ImportError as e:
        print(f"Enhanced logging not available: {e}")
    
    print("\n=== RESULTS ===")
    print("If you see colors in the ANSI test above, your terminal supports colors.")
    print("If the enhanced logging shows colors, the integration is working.")
    print("If you don't see colors, try running in:")
    print("- Windows Terminal (recommended)")
    print("- VSCode integrated terminal")
    print("- Or set DISABLE_LOG_COLORS=false in your .env file")


if __name__ == "__main__":
    test_terminal_colors()