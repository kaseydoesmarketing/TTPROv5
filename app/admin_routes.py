from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import sqlite3
import os
from .database import get_db
from .config import settings

router = APIRouter(prefix="/admin", tags=["admin"])

@router.post("/fix-sqlite-schema")
async def fix_sqlite_schema():
    """
    Emergency endpoint to fix SQLite database schema
    Fixes the 'unknown function: now()' error in youtube_channels table
    """
    try:
        db_paths = [
            './titletesterpro.db',
            '/app/titletesterpro.db',
            'titletesterpro.db',
            '/opt/render/project/src/titletesterpro.db'
        ]
        
        db_path = None
        for path in db_paths:
            if os.path.exists(path):
                db_path = path
                break
        
        if not db_path:
            return {
                "error": "SQLite database file not found",
                "searched_paths": db_paths,
                "current_dir": os.getcwd(),
                "files": [f for f in os.listdir('.') if f.endswith('.db')]
            }
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT sql FROM sqlite_master WHERE name='youtube_channels';")
        current_schema = cursor.fetchone()
        
        if not current_schema:
            return {"error": "youtube_channels table not found"}
        
        if "datetime('now')" in current_schema[0]:
            return {
                "status": "already_fixed",
                "message": "Schema already uses datetime('now')",
                "current_schema": current_schema[0]
            }
        
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
        
        cursor.execute("SELECT sql FROM sqlite_master WHERE name='youtube_channels';")
        updated_schema = cursor.fetchone()
        
        conn.close()
        
        return {
            "status": "success",
            "message": "SQLite schema fixed successfully",
            "database_path": db_path,
            "old_schema": current_schema[0],
            "new_schema": updated_schema[0] if updated_schema else None,
            "datetime_now_used": "datetime('now')" in (updated_schema[0] if updated_schema else "")
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "error_type": type(e).__name__
        }
