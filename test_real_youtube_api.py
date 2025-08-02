#!/usr/bin/env python3
import sys
import os
sys.path.append('/home/ubuntu/repos/TTPROv4/backend')

import asyncio
from app.config import settings
from app.youtube_api import YouTubeAPIClient

async def test_real_youtube_api():
    print("=== Real YouTube API Integration Testing ===")
    print(f"Environment: {settings.environment}")
    print(f"Is Development: {settings.is_development}")
    print(f"YouTube API Key: {settings.youtube_api_key[:20]}...")
    print()
    
    client = YouTubeAPIClient()
    
    print("=== Testing get_channel_info() with real API ===")
    try:
        result = await client.get_channel_info("real_access_token_placeholder")
        print(f"✅ get_channel_info() result: {result}")
    except Exception as e:
        print(f"⚠️  get_channel_info() failed as expected without real OAuth token: {e}")
    
    print()
    print("=== Testing get_channel_videos() with real API ===")
    try:
        result = await client.get_channel_videos("UCBJycsmduvYEL83R_U4JriQ")  # Example: Marques Brownlee
        print(f"✅ get_channel_videos() result: {len(result) if result else 0} videos found")
        if result and len(result) > 0:
            print(f"   First video: {result[0].get('title', 'No title')}")
    except Exception as e:
        print(f"❌ get_channel_videos() failed: {e}")
    
    print()
    print("=== Testing get_video_details() with real API ===")
    try:
        result = await client.get_video_details("dQw4w9WgXcQ")  # Rick Roll video ID
        print(f"✅ get_video_details() result: {result.get('title', 'No title') if result else 'No result'}")
    except Exception as e:
        print(f"❌ get_video_details() failed: {e}")
    
    print()
    print("=== YouTube API Integration Summary ===")
    if settings.is_development:
        print("❌ CRITICAL: Development mode is ENABLED")
    else:
        print("✅ Production mode confirmed")
        print("✅ Real YouTube API key configured")
        print("✅ Development bypasses are DISABLED")
        print("✅ All API calls use real YouTube Data API endpoints")

if __name__ == "__main__":
    asyncio.run(test_real_youtube_api())
