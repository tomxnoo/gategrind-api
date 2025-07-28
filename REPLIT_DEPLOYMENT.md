# Replit Deployment Guide

## Quick Setup

Your bot is now configured for production mode and ready to deploy on Replit!

### 1. Environment Variables
Make sure these are set to `false` in your `.env` file (already done):
```
DEV_MODE=false
DEVELOPMENT_MODE=false
```

### 2. Database Configuration
The bot is configured to use your Neon PostgreSQL database:
```
DATABASE_URL=postgresql://neondb_owner:npg_QPNvy9ORUwf7@ep-polished-frost-a9na50tb-pooler.gwc.azure.neon.tech/neondb?sslmode=require&channel_binding=require
```

### 3. Entry Point
The `main.py` file in the root directory is configured as the entry point for Replit.

### 4. Replit Configuration
The `.replit` file is already configured to:
- Run `python3 main.py`
- Use port 5000 (mapped to external port 80)
- Include necessary packages (postgresql, libsodium, etc.)

## Deployment Steps

1. **Upload to Replit**: Import your GitHub repository or upload the files
2. **Install Dependencies**: Replit should automatically install from `requirements.txt`
3. **Set Environment Variables**: Copy your `.env` file or set variables in Replit's secrets
4. **Run**: Click the "Run" button - it will execute `python3 main.py`

## Testing Production Mode Locally

To test production mode locally before deploying:

```bash
# Set environment variables and run
$env:DEV_MODE="false"; $env:DEVELOPMENT_MODE="false"; python main.py
```

The server will:
- Connect to the real PostgreSQL database
- Connect to Redis
- Run on port 5000 (or 8002 for local testing)
- Serve the awakening panel and all API endpoints

## Features Available in Production

✅ **Database Connection**: Full PostgreSQL with Neon  
✅ **Redis Caching**: For session management  
✅ **Awakening Panel**: Shadow ritual interface  
✅ **API Endpoints**: All V2 FastAPI routes  
✅ **Authentication**: JWT-based auth system  
✅ **Monitoring**: Sentry error tracking  
✅ **Logging**: Logfire integration  

## Troubleshooting

- **Port Issues**: Replit maps internal port 5000 to external port 80
- **Database**: Ensure Neon database is accessible and credentials are correct
- **Environment**: Make sure `DEV_MODE` and `DEVELOPMENT_MODE` are set to `false`
- **Dependencies**: Check that all packages in `requirements.txt` are installed

Your bot is ready for Replit deployment! 🚀