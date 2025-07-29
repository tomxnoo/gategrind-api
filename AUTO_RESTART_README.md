# Bot Auto-Restart System

This directory contains an automated restart system for the Discord bot that works seamlessly with Replit.

## Files

- `start.py` - Auto-restart wrapper script
- `.replit` - Updated to use the wrapper script
- `restart_signal` - Signal file created by restart command (auto-deleted)
- `stop_restart` - Create this file to disable auto-restart
- `restart.log` - Log file for restart events

## How It Works

1. **Auto-Restart Wrapper**: `start.py` runs the bot in a loop and automatically restarts it when it exits
2. **Restart Command**: Creates a `restart_signal` file and exits gracefully
3. **Rapid Restart Protection**: Prevents infinite restart loops with rate limiting
4. **Graceful Shutdown**: Handles signals properly for clean shutdowns

## Usage

### Normal Operation
- Click "Run" in Replit - the bot will start with auto-restart enabled
- The bot will automatically restart if it crashes or exits

### Manual Restart
- Use the Discord command: `!restart_bot` (owner only)
- The bot will restart automatically within 3 seconds

### Stop Auto-Restart
- Create a file named `stop_restart` in the project root
- Or use Ctrl+C in the Replit console

### Emergency Stop
- Use Ctrl+C in Replit console for immediate shutdown

## Features

- **Automatic Restart**: Bot restarts automatically on exit/crash
- **Rate Limiting**: Prevents rapid restart loops (max 5 restarts per minute)
- **Real-time Logging**: All bot output is streamed in real-time
- **Restart Logging**: Restart events are logged to `restart.log`
- **Signal Handling**: Proper handling of shutdown signals
- **Manual Control**: Easy ways to restart or stop the auto-restart

## Monitoring

Check `restart.log` for restart history and any issues:
```bash
tail -f restart.log
```