#!/usr/bin/env python3
"""
Check if the application is ready for Railway deployment
"""
import os
import sys
from typing import List, Tuple

def check_environment_variables() -> Tuple[bool, List[str]]:
    """Check if all required environment variables are set"""
    required_vars = {
        "DATABASE_URL": "PostgreSQL connection string (provided by Railway)",
        "REDIS_URL": "Redis connection string (provided by Railway)",
        "FIREBASE_PROJECT_ID": "Firebase project ID",
        "FIREBASE_PRIVATE_KEY": "Firebase service account private key",
        "FIREBASE_PRIVATE_KEY_ID": "Firebase private key ID",
        "FIREBASE_CLIENT_EMAIL": "Firebase client email",
        "FIREBASE_CLIENT_ID": "Firebase client ID",
        "GOOGLE_CLIENT_ID": "Google OAuth client ID",
        "GOOGLE_CLIENT_SECRET": "Google OAuth client secret",
        "YOUTUBE_API_KEY": "YouTube Data API key",
        "SECRET_KEY": "Application secret key for sessions"
    }
    
    missing_vars = []
    for var, description in required_vars.items():
        if not os.getenv(var):
            missing_vars.append(f"{var}: {description}")
    
    return len(missing_vars) == 0, missing_vars

def check_optional_variables() -> List[str]:
    """Check optional environment variables"""
    optional_vars = {
        "STRIPE_SECRET_KEY": "Stripe secret key (for payments)",
        "STRIPE_PUBLISHABLE_KEY": "Stripe publishable key",
        "STRIPE_WEBHOOK_SECRET": "Stripe webhook secret",
        "CORS_ORIGINS": "Allowed CORS origins (has default)",
        "ENVIRONMENT": "Environment name (defaults to production)"
    }
    
    missing_optional = []
    for var, description in optional_vars.items():
        if not os.getenv(var):
            missing_optional.append(f"{var}: {description}")
    
    return missing_optional

def main():
    print("🚂 Railway Deployment Readiness Check\n")
    
    # Check required variables
    all_set, missing_required = check_environment_variables()
    
    if missing_required:
        print("❌ Missing Required Environment Variables:")
        for var in missing_required:
            print(f"   - {var}")
        print("\n📝 Add these in Railway dashboard:")
        print("   1. Go to your service settings")
        print("   2. Click on 'Variables' tab")
        print("   3. Add each missing variable")
        print("\n⚠️  Note: DATABASE_URL and REDIS_URL are automatically set when you add PostgreSQL and Redis services to Railway")
    else:
        print("✅ All required environment variables are set!")
    
    # Check optional variables
    missing_optional = check_optional_variables()
    if missing_optional:
        print("\n⚠️  Optional Environment Variables (not set):")
        for var in missing_optional:
            print(f"   - {var}")
    
    # Check files
    print("\n📁 Checking deployment files...")
    required_files = [
        ("railway.toml", "Railway configuration"),
        ("railway.dockerfile", "Railway-specific Dockerfile"),
        ("start.sh", "Startup script"),
        ("requirements.txt", "Python dependencies"),
        ("alembic.ini", "Database migration config")
    ]
    
    missing_files = []
    for file, description in required_files:
        if not os.path.exists(file):
            missing_files.append(f"{file}: {description}")
    
    if missing_files:
        print("❌ Missing deployment files:")
        for file in missing_files:
            print(f"   - {file}")
    else:
        print("✅ All deployment files present!")
    
    # Summary
    print("\n" + "="*50)
    if all_set and not missing_files:
        print("✅ Your app is ready for Railway deployment!")
        print("\nNext steps:")
        print("1. Push your code to GitHub")
        print("2. Connect your repo to Railway")
        print("3. Add PostgreSQL and Redis services")
        print("4. Deploy!")
        return 0
    else:
        print("❌ Your app needs configuration before Railway deployment")
        print("\nRefer to RAILWAY_SETUP.md for detailed instructions")
        return 1

if __name__ == "__main__":
    sys.exit(main())