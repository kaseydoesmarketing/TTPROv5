#!/usr/bin/env python3
"""
SQLite database schema fix for production database
Fixes the "unknown function: now()" error by updating youtube_channels table
"""

import sqlite3
import os
import sys

def main():
    print("🔧 SQLite Database Schema Fix")
    
    db_paths = ['./titletesterpro.db', '/app/titletesterpro.db']
    db_path = None
    
    for path in db_paths:
        if os.path.exists(path):
            db_path = path
            break
    
    if not db_path:
        print("❌ SQLite database file not found at expected locations:")
        for path in db_paths:
            print(f"  - {path}")
        return False
    
    print(f"📁 Found database at: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("✅ Connected to SQLite database")
        
        print("\n📋 Checking current youtube_channels table schema...")
        cursor.execute("SELECT sql FROM sqlite_master WHERE name='youtube_channels';")
        current_schema = cursor.fetchone()
        if current_schema:
            print("Current table schema:")
            print(current_schema[0])
        else:
            print("❌ youtube_channels table not found!")
            return False
        
        print("\n🔄 Applying SQLite schema fix...")
        
        cursor.executescript("""
        BEGIN TRANSACTION;
        
        CREATE TABLE youtube_channels_new (
            id VARCHAR NOT NULL, 
            user_id VARCHAR NOT NULL, 
            channel_id VARCHAR NOT NULL, 
            channel_title VARCHAR NOT NULL, 
            channel_description TEXT, 
            subscriber_count INTEGER DEFAULT 0, 
            video_count INTEGER DEFAULT 0, 
            view_count INTEGER DEFAULT 0, 
            thumbnail_url VARCHAR, 
            custom_url VARCHAR, 
            is_active BOOLEAN DEFAULT 1, 
            is_selected BOOLEAN DEFAULT 0, 
            created_at DATETIME DEFAULT (datetime('now')), 
            updated_at DATETIME DEFAULT (datetime('now')), 
            PRIMARY KEY (id), 
            FOREIGN KEY(user_id) REFERENCES users (id)
        );
        
        INSERT INTO youtube_channels_new SELECT * FROM youtube_channels;
        DROP TABLE youtube_channels;
        ALTER TABLE youtube_channels_new RENAME TO youtube_channels;
        CREATE UNIQUE INDEX ix_youtube_channels_channel_id ON youtube_channels (channel_id);
        
        COMMIT;
        """)
        
        print("✅ SQLite schema fixed successfully")
        
        print("\n🔍 Verifying updated schema...")
        cursor.execute("SELECT sql FROM sqlite_master WHERE name='youtube_channels';")
        updated_schema = cursor.fetchone()
        if updated_schema:
            print("Updated table schema:")
            print(updated_schema[0])
            
            if "datetime('now')" in updated_schema[0]:
                print("✅ Confirmed: datetime('now') is now used for default values")
            else:
                print("⚠️  Warning: datetime('now') not found in schema")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        try:
            cursor.execute("ROLLBACK;")
        except:
            pass
        return False
        
    finally:
        try:
            conn.close()
            print("🔌 Database connection closed")
        except:
            pass

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
