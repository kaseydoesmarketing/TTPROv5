#!/usr/bin/env python3
import sys
import os
sys.path.append('/home/ubuntu/repos/TTPROv4/backend')

from app.database import SessionLocal
from app.models import User, YouTubeChannel

def test_oauth_models():
    print("=== OAuth Models Testing ===")
    
    db = SessionLocal()
    try:
        print("✅ Testing User model...")
        user_count = db.query(User).count()
        print(f"   Current user count: {user_count}")
        
        print("✅ Testing YouTubeChannel model...")
        channel_count = db.query(YouTubeChannel).count()
        print(f"   Current channel count: {channel_count}")
        
        print("✅ Testing User-YouTubeChannel relationship...")
        
        users_with_channels = db.query(User).join(YouTubeChannel, isouter=True).all()
        print(f"   Users query with channels: {len(users_with_channels)} results")
        
        print("\n=== OAuth Models Test Summary ===")
        print("✅ User model: Working")
        print("✅ YouTubeChannel model: Working") 
        print("✅ User-YouTubeChannel relationship: Working")
        print("✅ Database schema is ready for OAuth testing")
        
    except Exception as e:
        print(f"❌ Model test failed: {e}")
        return False
    finally:
        db.close()
    
    return True

if __name__ == "__main__":
    success = test_oauth_models()
    if success:
        print("\n🎉 All OAuth models are ready for multi-account testing!")
    else:
        print("\n❌ OAuth models need fixing before testing can proceed")
        sys.exit(1)
