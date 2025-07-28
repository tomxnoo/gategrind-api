#!/usr/bin/env python3
"""
REALM OF SHADOWS - PRODUCTION ENTRY POINT
==========================================
This is the main entry point for production deployment on Replit.
It starts the FastAPI V2 application server.
"""

import os
import sys
from pathlib import Path

# Add the app directory to the Python path
app_dir = Path(__file__).parent / "app"
sys.path.insert(0, str(app_dir))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

import uvicorn

if __name__ == "__main__":
    # Import the FastAPI app from the app directory
    from main import app
    
    # Get configuration from environment
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "5000"))  # Default to 5000 for Replit
    
    print(f"🚀 Starting FastAPI V2 Application")
    print(f"🌐 Host: {host}")
    print(f"🔌 Port: {port}")
    
    # Start the server
    uvicorn.run(
        app,
        host=host,
        port=port,
        reload=False  # Set to False for production
    )