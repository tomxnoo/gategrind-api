import secrets

# Generate a secure JWT secret key
jwt_secret = secrets.token_urlsafe(32)

print("Add this to your .env file:")
print(f"JWT_SECRET_KEY={jwt_secret}")
print("\n⚠️  Keep this secret secure and never commit it to version control!")