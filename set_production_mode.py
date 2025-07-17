"""
Script to set production mode environment variables
"""
import os

# Set production environment variables
production_vars = {
    "DEV_MODE": "false",
    "DEVELOPMENT_MODE": "false",
    "JWT_SECRET_KEY": "your-production-secret-key-here",  # Change this!
    "API_BASE_URL": "http://localhost:8000/api"  # Or your production URL
}

print("Setting production mode environment variables...")
for key, value in production_vars.items():
    os.environ[key] = value
    print(f"Set {key}={value}")

print("\n✅ Production mode configured!")
print("⚠️  Remember to set JWT_SECRET_KEY to a secure value in your .env file!")