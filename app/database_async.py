"""
Non-blocking database connection management for Railway deployments
Allows FastAPI app to start immediately while connecting to database in background
"""

import asyncio
import logging
from typing import Optional, Any
from contextlib import asynccontextmanager
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base  
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import OperationalError
from .config import settings

logger = logging.getLogger(__name__)

# Create base for models
Base = declarative_base()

class AsyncDatabaseManager:
    """Non-blocking database manager for Railway health checks"""
    
    def __init__(self):
        self.engine: Optional[Any] = None
        self.SessionLocal: Optional[Any] = None
        self.is_connected = False
        self.connection_task: Optional[asyncio.Task] = None
        
    async def initialize_in_background(self):
        """Initialize database connection in background without blocking startup"""
        logger.info("🔄 Starting background database connection...")
        
        try:
            # Create engine with short timeout
            database_url = settings.database_url
            if not database_url:
                logger.error("❌ DATABASE_URL not configured")
                return False
                
            # Create engine with aggressive timeout settings
            connect_args = {}
            if "postgresql" in database_url:
                connect_args = {
                    "connect_timeout": 10,
                    "options": "-c statement_timeout=10000"
                }
            
            self.engine = create_engine(
                database_url,
                pool_timeout=10,
                pool_recycle=300,
                pool_pre_ping=True,
                connect_args=connect_args,
                echo=False
            )
            
            # Create session factory
            self.SessionLocal = sessionmaker(
                bind=self.engine,
                autocommit=False,
                autoflush=False
            )
            
            # Test connection with timeout
            await asyncio.wait_for(
                self._test_connection(), 
                timeout=10.0
            )
            
            self.is_connected = True
            logger.info("✅ Database connected successfully in background")
            return True
            
        except asyncio.TimeoutError:
            logger.warning("⚠️ Database connection timeout - app will continue without DB")
            return False
        except Exception as e:
            logger.warning(f"⚠️ Database connection failed: {e} - app will continue")
            return False
    
    async def _test_connection(self):
        """Test database connection in async context"""
        def _sync_test():
            from sqlalchemy import text
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1")).fetchone()
        
        # Run sync operation in thread pool
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, _sync_test)
    
    def get_db_session(self):
        """Get database session if available, otherwise return None"""
        if not self.is_connected or not self.SessionLocal:
            return None
        return self.SessionLocal()

# Global database manager instance
db_async = AsyncDatabaseManager()

def get_db():
    """Dependency function for FastAPI - returns session or raises if unavailable"""
    session = db_async.get_db_session()
    if session is None:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=503, 
            detail="Database temporarily unavailable"
        )
    try:
        yield session
    finally:
        session.close()

def get_db_optional():
    """Optional database dependency - returns None if database unavailable"""
    session = db_async.get_db_session()
    if session:
        try:
            yield session
        finally:
            session.close()
    else:
        yield None

# Background task management
async def start_database_connection():
    """Start database connection in background"""
    if not db_async.connection_task:
        db_async.connection_task = asyncio.create_task(
            db_async.initialize_in_background()
        )
    return db_async.connection_task

def is_database_ready() -> bool:
    """Check if database is ready"""
    return db_async.is_connected