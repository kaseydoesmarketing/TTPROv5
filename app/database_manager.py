"""
Robust database connection management with pooling and retry logic
Handles all PostgreSQL connection failures gracefully
"""

import logging
import time
from typing import Optional, Dict, Any
from contextlib import contextmanager
from functools import wraps
from sqlalchemy import create_engine, event, text, pool
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import (
    OperationalError, 
    DisconnectionError, 
    TimeoutError,
    DatabaseError,
    InterfaceError
)
from urllib.parse import urlparse

from .config import settings

logger = logging.getLogger(__name__)

# Database connection retry configuration
RETRY_CONFIG = {
    "max_retries": 5,
    "initial_delay": 0.5,
    "max_delay": 30.0,
    "backoff_multiplier": 2.0,
    "jitter": 0.1
}

# Connection pool configuration
POOL_CONFIG = {
    "pool_size": 10,
    "max_overflow": 20,
    "pool_timeout": 30,
    "pool_recycle": 3600,  # 1 hour
    "pool_pre_ping": True
}

class DatabaseConnectionManager:
    """Manages database connections with automatic retry and recovery"""
    
    def __init__(self):
        self.engine: Optional[Any] = None
        self.SessionLocal: Optional[Any] = None
        self.Base = declarative_base()
        self.connection_healthy = False
        self.last_health_check = 0
        self.health_check_interval = 30  # seconds
        
    def create_engine_with_retry(self) -> bool:
        """Create database engine with comprehensive error handling"""
        try:
            database_url = settings.database_url
            
            if not database_url:
                logger.error("❌ DATABASE_URL not configured")
                return False
            
            # Parse database URL to determine type
            # Railway uses 'postgresql://' format
            parsed = urlparse(database_url)
            is_postgresql = parsed.scheme in ['postgresql', 'postgres', 'postgresql+psycopg', 'postgresql+psycopg2']
            
            if is_postgresql:
                logger.info("🔗 Configuring PostgreSQL connection with pooling...")
                
                # PostgreSQL-specific configuration
                engine_kwargs = {
                    "poolclass": pool.QueuePool,
                    "pool_size": POOL_CONFIG["pool_size"],
                    "max_overflow": POOL_CONFIG["max_overflow"],
                    "pool_timeout": POOL_CONFIG["pool_timeout"],
                    "pool_recycle": POOL_CONFIG["pool_recycle"],
                    "pool_pre_ping": POOL_CONFIG["pool_pre_ping"],
                    "echo": False,  # Disable SQL logging in production
                    "echo_pool": False,
                    "connect_args": {
                        "connect_timeout": 10,
                        "options": "-c statement_timeout=30000"  # 30 second timeout
                    }
                }
            else:
                logger.info("🔗 Configuring SQLite connection...")
                # SQLite configuration
                engine_kwargs = {
                    "poolclass": pool.StaticPool,
                    "connect_args": {"check_same_thread": False},
                    "echo": False
                }
            
            # Create engine with retry logic
            for attempt in range(RETRY_CONFIG["max_retries"]):
                try:
                    self.engine = create_engine(database_url, **engine_kwargs)
                    
                    # Test connection
                    with self.engine.connect() as conn:
                        conn.execute(text("SELECT 1"))
                    
                    # Create session factory
                    self.SessionLocal = sessionmaker(
                        autocommit=False, 
                        autoflush=False, 
                        bind=self.engine
                    )
                    
                    # Set up connection event listeners
                    self._setup_connection_events()
                    
                    self.connection_healthy = True
                    logger.info("✅ Database connection established successfully")
                    return True
                    
                except Exception as e:
                    delay = min(
                        RETRY_CONFIG["initial_delay"] * (RETRY_CONFIG["backoff_multiplier"] ** attempt),
                        RETRY_CONFIG["max_delay"]
                    )
                    
                    logger.warning(f"⚠️ Database connection attempt {attempt + 1} failed: {e}")
                    
                    if attempt < RETRY_CONFIG["max_retries"] - 1:
                        logger.info(f"🔄 Retrying in {delay:.1f} seconds...")
                        time.sleep(delay)
                    else:
                        logger.error("❌ All database connection attempts failed")
                        return False
                        
        except Exception as e:
            logger.error(f"❌ Database engine creation failed: {e}")
            return False
    
    def _setup_connection_events(self):
        """Set up SQLAlchemy event listeners for connection monitoring"""
        if not self.engine:
            return
            
        @event.listens_for(self.engine, "connect")
        def receive_connect(dbapi_connection, connection_record):
            logger.debug("📡 New database connection established")
        
        @event.listens_for(self.engine, "checkout")
        def receive_checkout(dbapi_connection, connection_record, connection_proxy):
            logger.debug("🔄 Database connection checked out from pool")
        
        @event.listens_for(self.engine, "checkin")
        def receive_checkin(dbapi_connection, connection_record):
            logger.debug("✅ Database connection returned to pool")
        
        @event.listens_for(self.engine, "invalidate")
        def receive_invalidate(dbapi_connection, connection_record, exception):
            logger.warning(f"❌ Database connection invalidated: {exception}")
            self.connection_healthy = False
    
    def test_connection(self, timeout: float = 5.0) -> bool:
        """Test database connection health"""
        if not self.engine:
            return False
            
        try:
            with self.engine.connect() as conn:
                # Set a statement timeout for the test query
                if "postgresql" in str(self.engine.url):
                    conn.execute(text(f"SET statement_timeout = {int(timeout * 1000)}"))
                
                result = conn.execute(text("SELECT 1 as health_check"))
                row = result.fetchone()
                
                if row and row[0] == 1:
                    self.connection_healthy = True
                    self.last_health_check = time.time()
                    return True
                    
        except Exception as e:
            logger.warning(f"⚠️ Database health check failed: {e}")
            self.connection_healthy = False
            
        return False
    
    def get_session_with_retry(self) -> Optional[Session]:
        """Get database session with automatic retry logic"""
        if not self.SessionLocal:
            logger.error("❌ Database not initialized")
            return None
        
        for attempt in range(RETRY_CONFIG["max_retries"]):
            try:
                session = self.SessionLocal()
                
                # Test the session with a simple query
                session.execute(text("SELECT 1"))
                return session
                
            except (OperationalError, DisconnectionError, InterfaceError) as e:
                logger.warning(f"⚠️ Session creation attempt {attempt + 1} failed: {e}")
                
                if attempt < RETRY_CONFIG["max_retries"] - 1:
                    delay = min(
                        RETRY_CONFIG["initial_delay"] * (RETRY_CONFIG["backoff_multiplier"] ** attempt),
                        RETRY_CONFIG["max_delay"]
                    )
                    time.sleep(delay)
                    
                    # Try to recreate the engine if connection is completely broken
                    if attempt >= 2:
                        logger.info("🔄 Attempting to recreate database connection...")
                        self.create_engine_with_retry()
                else:
                    logger.error("❌ All session creation attempts failed")
                    return None
            except Exception as e:
                logger.error(f"❌ Unexpected session creation error: {e}")
                return None
        
        return None
    
    @contextmanager
    def get_db_session(self):
        """Context manager for database sessions with automatic cleanup"""
        session = self.get_session_with_retry()
        if not session:
            raise DatabaseError("Failed to create database session")
        
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"❌ Database session error: {e}")
            raise
        finally:
            session.close()
    
    def get_connection_status(self) -> Dict[str, Any]:
        """Get detailed connection status information"""
        if not self.engine:
            return {
                "status": "not_initialized",
                "healthy": False,
                "pool_info": None,
                "last_check": None
            }
        
        # Get pool information
        pool_info = {}
        if hasattr(self.engine.pool, 'size'):
            pool_info = {
                "pool_size": self.engine.pool.size(),
                "checked_in": self.engine.pool.checkedin(),
                "checked_out": self.engine.pool.checkedout(),
                "overflow": self.engine.pool.overflow(),
                "invalid": getattr(self.engine.pool, 'invalid', lambda: 0)()
            }
        
        # Check if we need to refresh health status
        current_time = time.time()
        if current_time - self.last_health_check > self.health_check_interval:
            self.test_connection()
        
        return {
            "status": "healthy" if self.connection_healthy else "unhealthy",
            "healthy": self.connection_healthy,
            "pool_info": pool_info,
            "last_check": self.last_health_check,
            "database_url_type": str(self.engine.url).split("://")[0] if self.engine else None
        }

# Global database manager instance
db_manager = DatabaseConnectionManager()

def get_db():
    """Dependency for FastAPI routes - provides database session with retry logic"""
    session = db_manager.get_session_with_retry()
    if not session:
        raise DatabaseError("Database session unavailable")
    
    try:
        yield session
    finally:
        session.close()

def retry_on_database_error(max_retries: int = 3, delay: float = 1.0):
    """Decorator to retry database operations on connection errors"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except (OperationalError, DisconnectionError, TimeoutError) as e:
                    last_exception = e
                    logger.warning(f"⚠️ Database operation retry {attempt + 1}/{max_retries}: {e}")
                    
                    if attempt < max_retries - 1:
                        time.sleep(delay * (1.5 ** attempt))  # Exponential backoff
                except Exception as e:
                    # Don't retry on non-connection errors
                    logger.error(f"❌ Non-retryable database error: {e}")
                    raise
            
            # If we get here, all retries failed
            logger.error(f"❌ Database operation failed after {max_retries} retries")
            raise last_exception
        
        return wrapper
    return decorator

def initialize_database():
    """Initialize database connection and test it"""
    logger.info("🔗 Initializing database connection...")
    
    success = db_manager.create_engine_with_retry()
    if success:
        logger.info("✅ Database initialization completed")
    else:
        logger.error("❌ Database initialization failed")
    
    return success

# Backwards compatibility
def get_legacy_db():
    """Legacy database session getter for existing code"""
    return get_db()

# Export engine and session for backwards compatibility
def get_engine():
    """Get the database engine"""
    return db_manager.engine

def get_session_factory():
    """Get the session factory"""
    return db_manager.SessionLocal

# Base class for models
Base = db_manager.Base