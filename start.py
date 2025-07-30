#!/usr/bin/env python3
"""
Auto-restart wrapper for the Discord bot.
This script automatically restarts the bot when it exits, providing seamless operation in Replit.
"""

import os
import sys
import time
import subprocess
import signal
import logging
from pathlib import Path

# Add project root to path for imports
project_root = os.path.dirname(__file__)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Configure enhanced logging for better console readability
# Note: We configure this early, but may need to reconfigure after subprocess starts
try:
    from shared.utils.enhanced_logging import configure_project_logging
    configure_project_logging()
    print("* Enhanced logging configured for Bot Manager - WARN and ERROR messages will stand out!")
    
except ImportError:
    # Fallback to basic logging if enhanced logging is not available
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        handlers=[
                            logging.StreamHandler(sys.stdout),
                            logging.FileHandler('restart.log', mode='a')
                        ])
    print("* Enhanced logging not available, using basic logging for Bot Manager")

logger = logging.getLogger(__name__)


class BotManager:

    def __init__(self):
        self.should_restart = True
        self.restart_count = 0
        self.max_rapid_restarts = 5
        self.rapid_restart_window = 60  # seconds
        self.restart_times = []

        # Signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        # Ensure enhanced logging is properly configured
        self._reconfigure_enhanced_logging()
    
    def _reconfigure_enhanced_logging(self):
        """Reconfigure enhanced logging to ensure it's not overridden"""
        try:
            from shared.utils.enhanced_logging import configure_project_logging
            configure_project_logging()
        except ImportError:
            pass

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.should_restart = False
        sys.exit(0)

    def _check_rapid_restarts(self):
        """Check if we're restarting too rapidly"""
        now = time.time()
        # Remove old restart times outside the window
        self.restart_times = [
            t for t in self.restart_times
            if now - t < self.rapid_restart_window
        ]

        if len(self.restart_times) >= self.max_rapid_restarts:
            logger.error(
                f"Too many rapid restarts ({len(self.restart_times)} in {self.rapid_restart_window}s)"
            )
            logger.error("Waiting 60 seconds before next restart attempt...")
            time.sleep(60)
            self.restart_times.clear()

    def _check_restart_signal(self):
        """Check if a restart was requested via signal file"""
        restart_file = Path("restart_signal")
        if restart_file.exists():
            logger.info("Restart signal file detected, restarting bot...")
            restart_file.unlink()  # Remove the signal file
            return True
        return False

    def run_bot(self):
        """Run the main bot process"""
        # Reconfigure enhanced logging before each bot start
        self._reconfigure_enhanced_logging()
        
        logger.info("Starting Discord bot...")

        try:
            # Run the main bot script
            process = subprocess.Popen([sys.executable, "main.py"],
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.STDOUT,
                                       universal_newlines=True,
                                       bufsize=1)

            # Stream output in real-time
            for line in iter(process.stdout.readline, ''):
                print(line.rstrip())

            process.wait()
            return process.returncode

        except Exception as e:
            logger.error(f"Error running bot: {e}")
            return 1

    def start(self):
        """Main loop with auto-restart functionality"""
        logger.info("Bot Manager started - Auto-restart enabled")
        logger.info(
            "To stop auto-restart, create a file named 'stop_restart' or use Ctrl+C"
        )

        while self.should_restart:
            # Check for stop signal
            if Path("stop_restart").exists():
                logger.info("Stop restart signal detected, exiting...")
                break

            # Check for restart signal
            if self._check_restart_signal():
                logger.info("Manual restart requested")

            # Check rapid restart protection
            self._check_rapid_restarts()

            # Record restart time
            self.restart_times.append(time.time())
            self.restart_count += 1

            if self.restart_count > 1:
                logger.info(
                    f"Restarting bot (attempt #{self.restart_count})...")

            # Run the bot
            exit_code = self.run_bot()

            if exit_code == 0:
                logger.info("Bot exited normally")
            else:
                logger.warning(f"Bot exited with code {exit_code}")

            # Check if we should continue restarting
            if not self.should_restart:
                break

            # Brief pause before restart
            logger.info("Restarting in 3 seconds...")
            time.sleep(3)

        logger.info("Bot Manager stopped")


def main():
    """Entry point"""
    # Ensure we're in the correct directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)

    # Create bot manager and start
    manager = BotManager()

    try:
        manager.start()
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down...")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
