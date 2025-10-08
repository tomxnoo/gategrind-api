# Deployment Guide - TypeScript Discord Bot

## Prerequisites

- Node.js 18+ installed
- PostgreSQL database accessible
- Redis instance running
- Discord bot token

## Environment Setup

Create a `.env` file in the project root:

```env
# Discord
DISCORD_TOKEN=your_discord_bot_token_here

# Database
DATABASE_URL=postgresql://username:password@host:5432/database_name

# Redis
REDIS_URL=redis://localhost:6379/0

# API
API_PORT=8000

# Optional: Sentry DSN for error tracking
SENTRY_DSN=your_sentry_dsn_here
```

## Local Development

### Install Dependencies
```bash
npm install
```

### Build TypeScript
```bash
npm run build
```

### Run the Bot
```bash
# Production mode
npm start

# Development mode (auto-reload)
npm run dev

# Watch mode (auto-rebuild)
npm run watch
```

## Production Deployment

### Option 1: Replit

1. Import the repository to Replit
2. Set environment variables in Replit Secrets:
   - `DISCORD_TOKEN`
   - `DATABASE_URL`
   - `REDIS_URL`
3. Add to `.replit`:
```toml
run = "npm start"
language = "nodejs"

[nix]
channel = "stable-22_11"

[deployment]
run = ["npm", "start"]
```

4. Click "Run" or deploy with `replit deployments create`

### Option 2: Fly.io

1. Install Fly CLI: `curl -L https://fly.io/install.sh | sh`

2. Create `fly.toml`:
```toml
app = "gategrind-bot"
primary_region = "iad"

[build]
  builder = "heroku/buildpacks:20"

[env]
  NODE_ENV = "production"

[[services]]
  http_checks = []
  internal_port = 8000
  processes = ["app"]
  protocol = "tcp"
  script_checks = []
```

3. Set secrets:
```bash
fly secrets set DISCORD_TOKEN=your_token
fly secrets set DATABASE_URL=your_db_url
fly secrets set REDIS_URL=your_redis_url
```

4. Deploy:
```bash
fly deploy
```

### Option 3: Docker

1. Create `Dockerfile`:
```dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

EXPOSE 8000

CMD ["npm", "start"]
```

2. Build and run:
```bash
docker build -t gategrind-bot .
docker run -d \
  --env-file .env \
  -p 8000:8000 \
  gategrind-bot
```

### Option 4: Heroku

1. Create `Procfile`:
```
worker: npm start
web: npm start
```

2. Deploy:
```bash
heroku create gategrind-bot
heroku addons:create heroku-postgresql:mini
heroku addons:create heroku-redis:mini
heroku config:set DISCORD_TOKEN=your_token
git push heroku main
```

### Option 5: VPS (Ubuntu/Debian)

1. Install Node.js:
```bash
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
```

2. Clone and setup:
```bash
git clone https://github.com/tomxnoo/gategrind-api.git
cd gategrind-api
npm install
npm run build
```

3. Create systemd service `/etc/systemd/system/gategrind-bot.service`:
```ini
[Unit]
Description=Gategrind Discord Bot
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/gategrind-api
ExecStart=/usr/bin/npm start
Restart=on-failure
Environment=NODE_ENV=production

[Install]
WantedBy=multi-user.target
```

4. Start service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable gategrind-bot
sudo systemctl start gategrind-bot
```

## Database Setup

The bot expects certain tables to exist. Run migrations:

```sql
-- User profiles table
CREATE TABLE IF NOT EXISTS user_profiles (
    user_id BIGINT PRIMARY KEY,
    level INTEGER DEFAULT 1,
    xp INTEGER DEFAULT 0,
    total_xp INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Daily quests table
CREATE TABLE IF NOT EXISTS daily_quests (
    id SERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES user_profiles(user_id),
    quest_data JSONB,
    date DATE DEFAULT CURRENT_DATE,
    rerolled BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Buffs table
CREATE TABLE IF NOT EXISTS user_buffs (
    id SERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES user_profiles(user_id),
    buff_id VARCHAR(50),
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Add indexes
CREATE INDEX idx_user_quests_date ON daily_quests(user_id, date);
CREATE INDEX idx_user_buffs_active ON user_buffs(user_id, expires_at);
```

## Redis Setup

If you don't have Redis, you can:

1. **Local Redis:**
```bash
# Ubuntu/Debian
sudo apt-get install redis-server
sudo systemctl start redis

# macOS
brew install redis
brew services start redis
```

2. **Docker Redis:**
```bash
docker run -d -p 6379:6379 redis:7-alpine
```

3. **Cloud Redis:**
- Redis Labs (https://redis.com/cloud/)
- AWS ElastiCache
- Heroku Redis addon

## Monitoring

### Logs

Check logs based on deployment:

```bash
# Local
npm start

# Systemd
sudo journalctl -u gategrind-bot -f

# Docker
docker logs -f container_id

# Fly.io
fly logs

# Heroku
heroku logs --tail
```

### Health Check

The bot exposes a health endpoint:

```bash
curl http://localhost:8000/health
# Response: {"status":"ok","timestamp":"2024-01-01T00:00:00.000Z"}
```

## Troubleshooting

### Bot doesn't start
- Check Discord token is valid
- Verify database connection string
- Ensure Redis is accessible

### Commands not responding
- Check bot has MESSAGE_CONTENT intent enabled
- Verify bot permissions in Discord server
- Check logs for errors

### Database errors
- Verify tables exist (run migrations)
- Check connection pool settings
- Ensure database user has proper permissions

## Performance Tuning

### Database Connection Pool

Adjust in `src/main.ts`:
```typescript
this.dbPool = new Pool({
    connectionString: DATABASE_URL,
    min: 5,      // Increase for high load
    max: 20,     // Increase for high load
    connectionTimeoutMillis: 60000,
});
```

### Redis Configuration

For production, configure Redis persistence:
```bash
redis-cli CONFIG SET save "60 1000"
```

## Scaling

### Horizontal Scaling

The bot uses auto-sharding, so multiple instances can run:

```bash
# Instance 1 (shards 0-3)
SHARD_ID=0 SHARD_COUNT=8 npm start

# Instance 2 (shards 4-7)
SHARD_ID=4 SHARD_COUNT=8 npm start
```

### Vertical Scaling

For larger servers, increase resources:
- 2GB RAM for <10k users
- 4GB RAM for 10k-50k users
- 8GB RAM for 50k+ users

## Migration from Python

To switch from Python to TypeScript bot:

1. **Parallel Testing:** Run both bots in different servers
2. **Verify Data:** Ensure database compatibility
3. **Cutover:** 
   - Stop Python bot
   - Start TypeScript bot
   - Monitor for issues
4. **Rollback:** Keep Python version ready if needed

## Security Best Practices

1. **Never commit secrets** - Use environment variables
2. **Use HTTPS** for API endpoints
3. **Enable database SSL** in production
4. **Rotate tokens** regularly
5. **Monitor error rates** with Sentry
6. **Keep dependencies updated:** `npm audit fix`

## Support

- Check logs first
- Review MIGRATION-GUIDE.md
- Compare with Python implementation
- Open GitHub issue for bugs
