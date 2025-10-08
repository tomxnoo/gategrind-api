# Realm of Shadows - TypeScript Discord Bot

This is the TypeScript refactor of the Python-based Discord bot, maintaining 100% feature parity with the original implementation.

## Overview

The bot has been migrated from Python (discord.py/Pycord) to TypeScript (discord.js v14) while preserving all functionality, UI/UX, and visual elements.

## Project Structure

```
src/
├── main.ts                 # Main entry point and bot initialization
├── api/                    # Fastify API server
│   └── server.ts
├── features/               # Feature modules (cogs)
│   ├── system/            # System hub navigation
│   ├── awakening/         # Awakening system
│   ├── buffs/             # Buff management
│   ├── logging/           # Movement/fitness logging
│   ├── quests/            # Daily quests & weekly contracts
│   ├── user/              # User profiles & progression
│   ├── moderation/        # Moderation tools
│   ├── fitness/           # Fitness integrations
│   └── incursions/        # Dungeon system
├── shared/                # Shared utilities
│   └── utils/
│       └── headers.ts     # UI headers and styling
├── types/                 # TypeScript type definitions
│   └── index.ts
└── core/                  # Core functionality (future)
```

## Features Migrated

All features from the Python implementation have been migrated:

- ✅ **System Hub** - Main navigation and command center
- ✅ **Awakening System** - Character awakening and progression
- ✅ **Buff Management** - Active buffs and consumable items
- ✅ **Movement Logger** - Fitness activity tracking
- ✅ **Quest System** - Daily quests and weekly contracts
- ✅ **User Profiles** - Stats, levels, and progression
- ✅ **Moderation Tools** - Message management and admin commands
- ✅ **Fitness Integration** - Garmin and health app sync
- ✅ **Incursions** - Dungeon/challenge system

## Setup

### Prerequisites

- Node.js 18+ 
- TypeScript 5+
- PostgreSQL database
- Redis instance

### Installation

```bash
# Install dependencies
npm install

# Build TypeScript
npm run build

# Start the bot
npm start
```

### Development

```bash
# Run in development mode with ts-node
npm run dev

# Watch mode (auto-rebuild on changes)
npm run watch
```

### Environment Variables

Create a `.env` file with the following:

```env
DISCORD_TOKEN=your_discord_bot_token
DATABASE_URL=postgresql://user:pass@host:5432/dbname
REDIS_URL=redis://localhost:6379/0
API_PORT=8000
```

## Migration Notes

### Key Changes from Python to TypeScript

1. **Library Migration**
   - Python: `discord.py` / `Pycord`
   - TypeScript: `discord.js` v14

2. **Command System**
   - Python: `@commands.command()` decorators
   - TypeScript: Event-based message handlers

3. **Database**
   - Python: `asyncpg` with connection pool
   - TypeScript: `pg` (node-postgres) with Pool

4. **Redis**
   - Python: Custom `RedisCache` class
   - TypeScript: `redis` npm package

5. **API Server**
   - Python: `FastAPI` with `uvicorn`
   - TypeScript: `Fastify`

### UI/UX Preservation

All embeds, colors, and ANSI-styled messages have been preserved exactly as they appear in the Python version:

- ANSI color codes in code blocks
- Embed colors (dark_teal = 0x2B5B5A, etc.)
- Emoji usage and positioning
- Footer text and styling
- Dropdown menus and button interactions

### Feature Parity

Every command, interaction, and feature from the Python bot has been implemented in TypeScript:

| Python Command | TypeScript Equivalent | Status |
|---------------|----------------------|---------|
| `!hub` | `!hub` | ✅ Implemented |
| `!awakening` | `!awakening` | ✅ Implemented |
| `!buffs` | `!buffs` | ✅ Implemented |
| `!quests` | `!quests` | ✅ Implemented |
| `!profile` | `!profile` | ✅ Implemented |
| `!fitness` | `!fitness` | ✅ Implemented |
| `!incursions` | `!incursions` | ✅ Implemented |
| `!rr` (admin) | `!rr` (admin) | ✅ Implemented |

## Testing

The bot can be tested locally or deployed to the same environments as the Python version:

- Replit
- Fly.io
- Any Node.js hosting platform

## Architecture

The TypeScript bot maintains the same architectural patterns as the Python version:

- **Cog System**: Each feature is a separate "cog" (module) with its own setup function
- **Event-Driven**: Uses Discord.js event system for message and interaction handling
- **Database Pool**: Maintains persistent database connection pool
- **Redis Caching**: Uses Redis for caching user data and reducing database load
- **Dual Mode**: Runs both Discord bot and API server simultaneously

## Performance

TypeScript/Node.js benefits:
- Faster startup time compared to Python
- Lower memory footprint
- Better handling of concurrent connections
- Native async/await support

## Contributing

When adding new features, follow the existing cog pattern:

1. Create a new cog class in `src/features/[feature]/[feature]Cog.ts`
2. Implement `registerHandlers()` method for event handling
3. Export a `setup()` function
4. Add the cog to the extension list in `main.ts`

## License

Same license as the original Python implementation.
