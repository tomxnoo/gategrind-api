# Quick Start Guide - TypeScript Discord Bot

Get the TypeScript bot running in 5 minutes!

## Prerequisites

- Node.js 18+ installed
- Discord bot token
- PostgreSQL database (optional for basic testing)
- Redis instance (optional for basic testing)

## Step 1: Install Dependencies

```bash
npm install
```

This installs:
- `discord.js` - Discord API library
- `typescript` - TypeScript compiler
- `pg` - PostgreSQL client
- `redis` - Redis client
- `fastify` - HTTP server
- And more...

## Step 2: Configure Environment

Create a `.env` file in the project root:

```env
# Required
DISCORD_TOKEN=your_discord_bot_token_here

# Optional (for full functionality)
DATABASE_URL=postgresql://user:pass@localhost:5432/dbname
REDIS_URL=redis://localhost:6379/0
API_PORT=8000
```

### Getting a Discord Token

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application (or select existing)
3. Go to "Bot" section
4. Click "Reset Token" and copy it
5. Enable these intents:
   - ✅ Guilds
   - ✅ Guild Messages
   - ✅ Message Content

## Step 3: Build TypeScript

```bash
npm run build
```

This compiles TypeScript to JavaScript in the `dist/` directory.

## Step 4: Run the Bot

```bash
npm start
```

You should see:
```
🌒 Starting Realm of Shadows - Dual Mode (Fastify + Discord Bot)
============================================================
[INFO] Initializing database connection pool...
[OK] Database connection pool created successfully.
[INFO] Connecting to Redis...
[OK] Connected to Redis successfully.
[INFO] Loading Discord bot extensions...
[OK] system/systemHubCog
[OK] awakening/awakeningCog
[OK] buffs/buffsCog
...
[INFO] Starting Discord bot...
════════════════════════════════════════════════════════════
🌒 YourBot#1234 online • ID 1234567890
Guilds: 1  •  Extensions loaded
════════════════════════════════════════════════════════════
```

## Step 5: Test Commands

In your Discord server, try these commands:

```
!hub          - Open system hub
!awakening    - View awakening system
!buffs        - Check active buffs
!quests       - See daily quests
!profile      - View your profile
!fitness      - Fitness integration
!incursions   - View incursions/dungeons
```

## Development Mode

For development with auto-reload:

```bash
npm run dev
```

Or watch mode (auto-rebuild on file changes):

```bash
npm run watch
# In another terminal:
npm start
```

## Troubleshooting

### "Bot not responding to commands"

1. Check bot has MESSAGE_CONTENT intent enabled in Discord Developer Portal
2. Verify bot has permissions in your server
3. Check console for error messages
4. Ensure bot is online (check user list)

### "Cannot connect to database"

If you don't have PostgreSQL:
1. Comment out database code in `src/main.ts`
2. Or use a free PostgreSQL instance:
   - [Supabase](https://supabase.com) - Free tier
   - [ElephantSQL](https://www.elephantsql.com) - Free plan
   - [Neon](https://neon.tech) - Free tier

### "Cannot connect to Redis"

If you don't have Redis:
1. Comment out Redis code in `src/main.ts`
2. Or use a free Redis instance:
   - [Redis Cloud](https://redis.com/cloud/) - Free tier
   - Or run locally: `docker run -d -p 6379:6379 redis:7-alpine`

### "Port 8000 already in use"

Change the port in `.env`:
```env
API_PORT=8001
```

## Next Steps

### Add Bot to Your Server

Use this invite link (replace CLIENT_ID with your bot's client ID):

```
https://discord.com/api/oauth2/authorize?client_id=YOUR_CLIENT_ID&permissions=8&scope=bot
```

Get your client ID from Discord Developer Portal → General Information → Application ID

### Explore Features

Read the documentation:
- `README-TYPESCRIPT.md` - Full TypeScript bot documentation
- `MIGRATION-GUIDE.md` - Technical details and patterns
- `DEPLOYMENT.md` - Production deployment options
- `SIDE-BY-SIDE-COMPARISON.md` - Python vs TypeScript examples
- `VISUAL-COMPARISON.md` - UI/UX details

### Customize

Edit cog files in `src/features/`:
- `system/systemHubCog.ts` - Main hub
- `awakening/awakeningCog.ts` - Awakening system
- `buffs/buffsCog.ts` - Buff management
- etc.

After making changes:
```bash
npm run build
npm start
```

## Common Commands

```bash
# Install dependencies
npm install

# Build TypeScript
npm run build

# Start bot (production)
npm start

# Start bot (development with auto-reload)
npm run dev

# Watch mode (auto-rebuild)
npm run watch

# Lint code
npm run lint

# Clean build directory
npm run clean
```

## File Structure Quick Reference

```
src/
├── main.ts              # Bot entry point
├── api/                 # HTTP server
├── features/            # Bot features (cogs)
│   ├── system/         # System hub (!hub)
│   ├── awakening/      # Awakening (!awakening)
│   ├── buffs/          # Buffs (!buffs)
│   ├── quests/         # Quests (!quests)
│   ├── user/           # User profiles (!profile)
│   ├── fitness/        # Fitness integration
│   ├── incursions/     # Dungeons (!incursions)
│   ├── logging/        # Movement logging
│   └── moderation/     # Admin tools
├── shared/utils/       # Shared utilities
├── core/               # Core functionality
└── types/              # TypeScript types
```

## Need Help?

1. Check the console for error messages
2. Review documentation files
3. Compare with Python implementation in `features/` (Python files)
4. Open a GitHub issue

## Success Checklist

- ✅ Node.js installed
- ✅ Dependencies installed (`npm install`)
- ✅ `.env` file created with DISCORD_TOKEN
- ✅ TypeScript built (`npm run build`)
- ✅ Bot starts without errors
- ✅ Bot appears online in Discord
- ✅ Commands respond (!hub works)

**You're ready to go!** 🎉

---

**Quick Reference:**

| Command | Description |
|---------|-------------|
| `npm install` | Install dependencies |
| `npm run build` | Compile TypeScript |
| `npm start` | Run bot |
| `npm run dev` | Development mode |
| `!hub` | Test bot command |

For production deployment, see `DEPLOYMENT.md`
