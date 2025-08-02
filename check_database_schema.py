#!/usr/bin/env python3
import sys
import os
sys.path.append('/home/ubuntu/repos/TTPROv4/backend')

from app.database import SessionLocal
from sqlalchemy import text

def check_database_schema():
    print("=== Database Schema Investigation ===")
    
    db = SessionLocal()
    try:
        result = db.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """))
        
        tables = [row[0] for row in result.fetchall()]
        print(f"Existing tables: {tables}")
        print()
        
        if 'youtube_channels' in tables:
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
        else:
            print("❌ youtube_channels table does NOT exist")
            print("This explains why the previous query failed")
        
        print()
        
        if 'users' in tables:
            result = db.execute(text("SELECT COUNT(*) FROM users"))
            user_count = result.fetchone()[0]
            print(f"✅ users table exists with {user_count} users")
        else:
            print("❌ users table does NOT exist")
            
        if 'alembic_version' in tables:
            result = db.execute(text("SELECT version_num FROM alembic_version"))
            version = result.fetchone()[0]
            print(f"✅ Current alembic version: {version}")
        else:
            print("❌ alembic_version table does NOT exist")
            
    except Exception as e:
        print(f"❌ Database query failed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_database_schema()
