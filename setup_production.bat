@echo off
echo Setting up production environment for awakening system...

REM Set your PostgreSQL database URL here
REM Format: postgresql+asyncpg://username:password@host:port/database
set DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/ros_trae_db

REM Disable development mode to use real database
set DEVELOPMENT_MODE=false
set DEV_MODE=false

REM Run database migrations if needed
echo Running database migrations...
alembic upgrade head

echo.
echo Environment configured for production mode!
echo Database URL: %DATABASE_URL%
echo Development Mode: %DEVELOPMENT_MODE%
echo.
echo Starting the bot...
python main_v1.py