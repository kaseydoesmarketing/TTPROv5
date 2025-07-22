#!/usr/bin/env python3
import sys
import os
sys.path.append('/home/ubuntu/repos/TTPROv4/backend')

from app.config import settings

print("=== Environment Configuration Audit ===")
print(f"Environment: {settings.environment}")
print(f"Is Development: {settings.is_development}")
print(f"Is Production: {settings.is_production}")
print()

print("=== Development Bypass Status ===")
if settings.is_development:
    print("⚠️  DEVELOPMENT MODE - Bypasses are ENABLED")
    print("   - Firebase 'dev-id-token' will be accepted")
    print("   - YouTube 'dev_access_token' will be accepted")
    print("   - Development user creation is enabled")
else:
    print("✅ PRODUCTION MODE - Bypasses are DISABLED")
    print("   - Only real Firebase tokens will be accepted")
    print("   - Only real YouTube access tokens will be accepted")
    print("   - No development user creation")

print()
print("=== Firebase Configuration ===")
firebase_fields = [
    'firebase_project_id',
    'firebase_private_key_id', 
    'firebase_client_email',
    'firebase_client_id'
]

for field in firebase_fields:
    value = getattr(settings, field, None)
    if value:
        print(f"✅ {field}: {'*' * min(len(str(value)), 20)}...")
    else:
        print(f"❌ {field}: NOT SET")

print()
print("=== YouTube API Configuration ===")
if settings.youtube_api_key:
    print(f"✅ youtube_api_key: {'*' * min(len(settings.youtube_api_key), 20)}...")
else:
    print("❌ youtube_api_key: NOT SET")
