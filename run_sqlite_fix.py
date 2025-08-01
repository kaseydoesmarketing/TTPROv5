#!/usr/bin/env python3
"""
Production SQLite database schema fix
This script will be deployed to Render to fix the database schema
"""

import sqlite3
import os
import sys

def main():
    print("🔧 Production SQLite Database Schema Fix")
    
    db_paths = [
        './titletesterpro.db',
        '/app/titletesterpro.db',
        'titletesterpro.db',
        '/opt/render/project/src/titletesterpro.db'
    ]
    
    db_path = None
    
    print("🔍 Searching for SQLite database file...")
    for path in db_paths:
        print(f"  Checking: {path}")
        if os.path.exists(path):
            db_path = path
            print(f"  ✅ Found database at: {path}")
            break
        else:
            print(f"  ❌ Not found: {path}")
    
    if not db_path:
        print("\n❌ SQLite database file not found at any expected location!")
        print("Available files in current directory:")
        try:
            for item in os.listdir('.'):
                if item.endswith('.db') or 'sqlite' in item.lower():
                    print(f"  - {item}")
        except Exception as e:
            print(f"  Error listing files: {e}")
        return False
    
    print(f"\n📁 Using database: {db_path}")
    
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
            
            if "datetime('now')" in current_schema[0]:
                print("✅ Schema already uses datetime('now') - fix may not be needed")
                return True
            else:
                print("❌ Schema uses incompatible datetime format - applying fix...")
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
                print("✅ SQLite compatibility issue resolved!")
            else:
                print("⚠️  Warning: datetime('now') not found in updated schema")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        try:
            cursor.execute("ROLLBACK;")
            print("🔄 Transaction rolled back")
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
    print("=" * 50)
    print("SQLite Database Schema Fix for Production")
    print("=" * 50)
    success = main()
    print("=" * 50)
    if success:
        print("🎉 Database schema fix completed successfully!")
        print("✅ The 'unknown function: now()' error should now be resolved")
    else:
        print("❌ Database schema fix failed!")
    print("=" * 50)
    sys.exit(0 if success else 1)
