
# Realm of Shadows — Discord Bot & Flask API
A unified codebase for running both your Discord bot and iOS Shortcuts-compatible Flask API on Fly.io or Replit.

## Quick Start

**On Replit:**
- Add your `DISCORD_TOKEN` and `DATABASE_URL` to Replit Secrets.
- Click "Run" or run: `poetry run python main.py`

**On Fly.io:**
- Set secrets with: `fly secrets set DISCORD_TOKEN=... DATABASE_URL=...`
- Deploy with: `fly deploy`

The Flask API runs on port 8080 and is public, ready for your iOS Shortcuts to POST data.

## Structure
- `main.py` — starts both Discord bot and Flask API together
- `api/flask_api.py` — your health data endpoints
- `cogs/` — all your Discord bot features
- `ui/` — UI logic (if any)
- `scripts/` — migration/utilities

---
