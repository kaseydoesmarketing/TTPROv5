#!/usr/bin/env python3
"""
Database schema fix for PostgreSQL production database
Adapts the SQLite commands provided by user to PostgreSQL syntax
"""

import os
import sys
from sqlalchemy import create_engine, text
from app.config import settings

def main():
    print("🔧 Database Schema Fix for PostgreSQL")
    print(f"Environment: {settings.environment}")
    print(f"Database URL: {settings.database_url[:50]}...")
    
    engine = create_engine(settings.database_url)
    
    try:
        with engine.connect() as conn:
            print("\n📋 Checking current youtube_channels table schema...")
            result = conn.execute(text("""
                SELECT column_name, data_type, column_default 
                FROM information_schema.columns 
                WHERE table_name = 'youtube_channels' 
                AND column_name IN ('created_at', 'updated_at')
                ORDER BY column_name;
            """))
            
            current_schema = result.fetchall()
            print("Current datetime columns:")
            for row in current_schema:
                print(f"  {row[0]}: {row[1]} DEFAULT {row[2]}")
            
            print("\n🔄 Applying PostgreSQL schema fix...")
            
            trans = conn.begin()
            
            try:
                conn.execute(text("""
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
                        is_active BOOLEAN DEFAULT true,
                        is_selected BOOLEAN DEFAULT false,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        PRIMARY KEY (id),
                        FOREIGN KEY(user_id) REFERENCES users (id)
                    );
                """))
                print("✅ Created new table with PostgreSQL datetime defaults")
                
                conn.execute(text("""
                    INSERT INTO youtube_channels_new 
                    SELECT * FROM youtube_channels;
                """))
                print("✅ Copied existing data")
                
                conn.execute(text("DROP TABLE youtube_channels;"))
                conn.execute(text("ALTER TABLE youtube_channels_new RENAME TO youtube_channels;"))
                print("✅ Replaced old table")
                
                conn.execute(text("""
                    CREATE UNIQUE INDEX ix_youtube_channels_channel_id 
                    ON youtube_channels (channel_id);
                """))
                print("✅ Recreated unique index")
                
                trans.commit()
                print("\n🎉 Database schema fix completed successfully!")
                
                print("\n🔍 Verifying updated schema...")
                result = conn.execute(text("""
                    SELECT column_name, data_type, column_default 
                    FROM information_schema.columns 
                    WHERE table_name = 'youtube_channels' 
                    AND column_name IN ('created_at', 'updated_at')
                    ORDER BY column_name;
                """))
                
                updated_schema = result.fetchall()
                print("Updated datetime columns:")
                for row in updated_schema:
                    print(f"  {row[0]}: {row[1]} DEFAULT {row[2]}")
                
            except Exception as e:
                trans.rollback()
                print(f"❌ Error during schema update: {e}")
                return False
                
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
