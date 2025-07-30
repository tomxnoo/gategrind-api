"""
Enhanced logging formatter with colors, visual separators, and improved readability.
Makes WARN and ERROR messages stand out from the console output wall of text.
"""

import logging
import sys
from typing import Optional


class ColoredFormatter(logging.Formatter):
    """Custom formatter that adds colors and visual separators for better readability."""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
        'RESET': '\033[0m',      # Reset
        'BOLD': '\033[1m',       # Bold
        'DIM': '\033[2m'         # Dim
    }
    
    # Visual separators for different log levels (Windows-compatible)
    SEPARATORS = {
        'DEBUG': '[DEBUG] ',
        'INFO': '[INFO] ',
        'WARNING': '[WARN] ',
        'ERROR': '[ERROR] ',
        'CRITICAL': '[CRITICAL] '
    }
    
    def __init__(self, use_colors: bool = None, compact: bool = False):
        """
        Initialize the colored formatter.
        
        Args:
            use_colors: Enable/disable colors. Auto-detect if None.
            compact: Use compact format for less verbose output.
        """
        if use_colors is None:
            # Auto-detect color support - improved Windows detection
            use_colors = (
                # Always enable colors if we detect a capable terminal
                'ANSICON' in os.environ or
                'WT_SESSION' in os.environ or  # Windows Terminal
                os.environ.get('TERM_PROGRAM') == 'vscode' or  # VSCode terminal
                'COLORTERM' in os.environ or
                # Fallback to TTY detection for non-Windows or if TTY is available
                (hasattr(sys.stdout, 'isatty') and sys.stdout.isatty() and sys.platform != 'win32')
            )
        
        self.use_colors = use_colors
        self.compact = compact
        
        # Choose format based on compact mode
        if compact:
            fmt = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        else:
            fmt = "%(asctime)s [%(levelname)s] %(name)s\n%(message)s"
            
        super().__init__(fmt, datefmt='%Y-%m-%d %H:%M:%S')
    
    def format(self, record: logging.LogRecord) -> str:
        """Format the log record with colors and visual improvements."""
        # Create a copy to avoid modifying the original record
        record_copy = logging.makeLogRecord(record.__dict__)
        
        # Get the base formatted message
        message = super().format(record_copy)
        
        if not self.use_colors:
            return self._add_separator(message, record.levelname)
        
        # Apply colors based on log level
        level_color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        
        # Special formatting for ERROR and CRITICAL
        if record.levelname in ['ERROR', 'CRITICAL']:
            # Add visual separator lines for errors
            separator_line = "=" * 80
            message = (
                f"\n{level_color}{self.COLORS['BOLD']}{separator_line}{self.COLORS['RESET']}\n"
                f"{level_color}{self.COLORS['BOLD']}{self._add_separator(message, record.levelname)}{self.COLORS['RESET']}\n"
                f"{level_color}{separator_line}{self.COLORS['RESET']}\n"
            )
        elif record.levelname == 'WARNING':
            # Add warning highlight
            message = (
                f"\n{level_color}{'-' * 60}{self.COLORS['RESET']}\n"
                f"{level_color}{self.COLORS['BOLD']}{self._add_separator(message, record.levelname)}{self.COLORS['RESET']}\n"
                f"{level_color}{'-' * 60}{self.COLORS['RESET']}\n"
            )
        else:
            # Standard formatting for INFO and DEBUG
            colored_message = f"{level_color}{message}{self.COLORS['RESET']}"
            message = self._add_separator(colored_message, record.levelname)
        
        return message
    
    def _add_separator(self, message: str, level: str) -> str:
        """Add visual separator based on log level."""
        separator = self.SEPARATORS.get(level, '• ')
        lines = message.split('\n')
        
        # Add separator to first line only to avoid cluttering multiline messages
        if lines:
            lines[0] = f"{separator}{lines[0]}"
        
        return '\n'.join(lines)


class EnhancedLogger:
    """Enhanced logger setup with improved console output."""
    
    @staticmethod
    def setup_enhanced_logging(
        level: str = 'INFO',
        use_colors: bool = None,
        compact: bool = False,
        log_file: Optional[str] = None
    ) -> None:
        """
        Set up enhanced logging with improved formatting.
        
        Args:
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            use_colors: Enable colors (auto-detect if None)
            compact: Use compact format
            log_file: Optional log file path
        """
        # Remove ALL existing handlers from root logger and common loggers
        loggers_to_reset = [
            logging.getLogger(),  # Root logger
            logging.getLogger('discord'),
            logging.getLogger('discord.ui.view'),
            logging.getLogger('sqlalchemy.engine'),
            logging.getLogger('uvicorn'),
            logging.getLogger('fastapi')
        ]
        
        for logger in loggers_to_reset:
            for handler in logger.handlers[:]:
                logger.removeHandler(handler)
            logger.propagate = True  # Ensure propagation to root
        
        # Set log level on root logger
        numeric_level = getattr(logging, level.upper(), logging.INFO)
        root_logger = logging.getLogger()
        root_logger.setLevel(numeric_level)
        
        # Create console handler with enhanced formatter
        console_handler = logging.StreamHandler(sys.stdout)
        console_formatter = ColoredFormatter(use_colors=use_colors, compact=compact)
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)
        
        # Add file handler if specified
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_formatter = ColoredFormatter(use_colors=False, compact=True)
            file_handler.setFormatter(file_formatter)
            root_logger.addHandler(file_handler)
        
        # Reduce noise from third-party libraries
        logging.getLogger('discord').setLevel(logging.WARNING)
        logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
        logging.getLogger('asyncio').setLevel(logging.WARNING)
        
        # Force reconfigure Discord.py and other library loggers
        EnhancedLogger.configure_library_loggers()
        
        # Test the enhanced logging
        logger = logging.getLogger('enhanced_logging')
        logger.info("Enhanced logging initialized successfully")
    
    @staticmethod
    def configure_library_loggers():
        """Force configure specific library loggers to use our enhanced formatting."""
        # Configure Discord.py loggers specifically
        discord_loggers = [
            'discord',
            'discord.ui.view',
            'discord.client',
            'discord.gateway',
            'discord.http'
        ]
        
        for logger_name in discord_loggers:
            logger = logging.getLogger(logger_name)
            logger.setLevel(logging.WARNING)  # Reduce Discord.py noise
            logger.propagate = True  # Ensure it uses root handler
            
        # Configure other library loggers
        other_loggers = {
            'sqlalchemy.engine': logging.WARNING,
            'uvicorn': logging.INFO,
            'fastapi': logging.INFO,
            'asyncio': logging.WARNING
        }
        
        for logger_name, level in other_loggers.items():
            logger = logging.getLogger(logger_name)
            logger.setLevel(level)
            logger.propagate = True


# Import os for environment variable check
import os


def configure_project_logging():
    """Configure enhanced logging for the RoS-TRAE project."""
    # Get environment variables
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    compact_logs = os.getenv('COMPACT_LOGS', 'false').lower() == 'true'
    disable_colors = os.getenv('DISABLE_LOG_COLORS', 'false').lower() == 'true'
    use_basic_logging = os.getenv('USE_BASIC_LOGGING', 'false').lower() == 'true'
    
    if use_basic_logging:
        # Use basic logging if requested
        logging.basicConfig(
            level=getattr(logging, log_level),
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[logging.StreamHandler()]
        )
    else:
        # Use enhanced logging
        EnhancedLogger.setup_enhanced_logging(
            level=log_level,
            use_colors=not disable_colors,
            compact=compact_logs,
            log_file='app.log'
        )


if __name__ == "__main__":
    # Demo the enhanced logging
    configure_project_logging()
    
    logger = logging.getLogger('demo')
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")
    
    # Demo multiline error
    try:
        raise ValueError("Example error for demonstration")
    except Exception as e:
        logger.error("An error occurred", exc_info=True)