#!/usr/bin/env python3
import sys
import os
sys.path.append('/home/ubuntu/repos/TTPROv4/backend')

from app.database import SessionLocal
from app.channel_models import YouTubeChannel
from sqlalchemy import text

def verify_youtube_channels_table():
    print("=== YouTube Channels Table Verification ===")
    
    db = SessionLocal()
    try:
        result = db.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name = 'youtube_channels';
        """))
        
        table_exists = result.fetchone()
        
        if table_exists:
            print("✅ youtube_channels table exists")
            
            result = db.execute(text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name = 'youtube_channels'
                ORDER BY ordinal_position;
            """))
            
            columns = result.fetchall()
            print("youtube_channels columns:")
            for col in columns:
                print(f"  - {col[0]} ({col[1]}, nullable: {col[2]})")
            
            print("\n=== Testing YouTubeChannel Model Operations ===")
            
            channel_count = db.query(YouTubeChannel).count()
            print(f"✅ Current channel count: {channel_count}")
            
            print("✅ YouTubeChannel model can query the database successfully")
            
        else:
            print("❌ youtube_channels table still does NOT exist")
            print("Migration may have failed or not been applied")
            
    except Exception as e:
        print(f"❌ Database operation failed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    verify_youtube_channels_table()
