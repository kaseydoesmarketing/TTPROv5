"""
Database connection with fallback and error handling
Handles Railway PostgreSQL failures gracefully
"""

import os
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from .config import settings
import time

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self.is_connected = False
        self.connection_attempts = 0
        self.max_retries = 3
        
    def create_engine_with_fallback(self):
        """Create database engine with connection pooling and error handling"""
        
        # Parse the database URL to check if it's PostgreSQL
        database_url = settings.database_url
        
        if not database_url:
            raise ValueError("DATABASE_URL environment variable is not set")
            
        logger.info(f"Attempting database connection to: {database_url.split('@')[0]}@...")
        
        # Configure connection pool for Railway PostgreSQL
        engine_kwargs = {
            "echo": False,  # Set to True for SQL debugging
            "pool_size": 5,
            "max_overflow": 10,
            "pool_pre_ping": True,  # Validates connections before use
            "pool_recycle": 300,    # Recycle connections every 5 minutes
            "connect_args": {
                "connect_timeout": 10,
                "application_name": "TitleTesterPro"
            }
        }
        
        # Handle PostgreSQL vs SQLite
        if database_url.startswith('postgresql://'):
            # Convert postgresql:// to postgresql+psycopg2://
            if database_url.startswith('postgresql://'):
                database_url = database_url.replace('postgresql://', 'postgresql+psycopg2://', 1)
                
            engine_kwargs["poolclass"] = QueuePool
            
        elif database_url.startswith('sqlite'):
            # Remove pool settings for SQLite
            engine_kwargs = {"echo": False}
            
        try:
            self.engine = create_engine(database_url, **engine_kwargs)
            
            # Test the connection
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            self.is_connected = True
            logger.info("✅ Database connection established successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            self.is_connected = False
            return False
    
    def get_session(self):
        """Get database session with retry logic"""
        if not self.is_connected:
            if not self.create_engine_with_fallback():
                raise Exception("Database connection failed after retries")
                
        return self.SessionLocal()
    
    def health_check(self):
        """Check database health"""
        try:
            if not self.engine:
                return False
                
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            self.is_connected = False
            return False
    
    def retry_connection(self):
        """Retry database connection with exponential backoff"""
        for attempt in range(self.max_retries):
            logger.info(f"Database connection attempt {attempt + 1}/{self.max_retries}")
            
            if self.create_engine_with_fallback():
                return True
                
            if attempt < self.max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                logger.info(f"Waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)
        
        logger.error("❌ All database connection attempts failed")
        return False

# Global database manager instance
db_manager = DatabaseManager()

# Initialize database connection
try:
    db_manager.create_engine_with_fallback()
except Exception as e:
    logger.error(f"Initial database connection failed: {e}")

# Legacy compatibility
Base = declarative_base()

def get_db():
    """Get database session with error handling"""
    try:
        db = db_manager.get_session()
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        # Try to reconnect
        if db_manager.retry_connection():
            db = db_manager.get_session()
            yield db
        else:
            raise
    finally:
        try:
            db.close()
        except:
            pass

def get_engine():
    """Get database engine"""
    if not db_manager.engine:
        db_manager.create_engine_with_fallback()
    return db_manager.engine