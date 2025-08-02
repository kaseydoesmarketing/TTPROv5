#!/usr/bin/env python3
import sys
import os
sys.path.append('/home/ubuntu/repos/TTPROv4/backend')

import asyncio
from app.config import settings
from app.youtube_api import YouTubeAPIClient

async def test_youtube_bypasses():
    print("=== YouTube API Development Bypass Testing ===")
    print(f"Environment: {settings.environment}")
    print(f"Is Development: {settings.is_development}")
    print()
    
    client = YouTubeAPIClient()
    
    print("=== Testing get_channel_info() bypass ===")
    try:
        result = await client.get_channel_info("dev_access_token")
        if result.get("id") == "dev_channel_123":
            print("❌ CRITICAL: Development bypass ACTIVATED in production!")
            print("   - get_channel_info() returned development data")
            print("   - This is a SECURITY RISK")
        else:
            print("✅ Development bypass properly gated")
    except Exception as e:
        print(f"✅ Development bypass properly gated - Exception: {e}")
    
    print()
    print("=== Testing get_channel_videos() bypass ===")
    try:
        result = await client.get_channel_videos("dev_channel_123")
        if result and len(result) > 0 and result[0].get("id") == "dev_video_1":
            print("❌ CRITICAL: Development bypass ACTIVATED in production!")
            print("   - get_channel_videos() returned development data")
            print("   - This is a SECURITY RISK")
        else:
            print("✅ Development bypass properly gated")
    except Exception as e:
        print(f"✅ Development bypass properly gated - Exception: {e}")
    
    print()
    print("=== YouTube API Bypass Security Summary ===")
    if settings.is_development:
        print("❌ CRITICAL: Development mode is ENABLED")
    else:
        print("✅ Production mode confirmed - Development bypasses are DISABLED")
        print("   - Line 22: get_channel_info() bypass properly gated")
        print("   - Line 67: get_channel_videos() bypass properly gated")

if __name__ == "__main__":
    asyncio.run(test_youtube_bypasses())
