"""
Test script to run only the FastAPI server for development/testing
"""
import os
import uvicorn

if __name__ == "__main__":
    # Set development mode to skip database/redis connections
    os.environ["DEV_MODE"] = "true"
    
    print("🌒 Starting FastAPI Server Only (Development Mode)")
    print("=" * 50)
    print("FastAPI server will be available at: http://localhost:8000")
    print("API documentation at: http://localhost:8000/docs")
    print("Development mode: Database and Redis connections disabled")
    print("Press Ctrl+C to stop")
    print("=" * 50)
    
    uvicorn.run(
        "api.main:app",  # Use import string instead of app object
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload on code changes
        log_level="info"
    )