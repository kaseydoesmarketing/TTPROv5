"""
Database configuration with robust connection management
Uses the enhanced database manager for production reliability
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings
from .database_manager import (
    db_manager, 
    get_db, 
    initialize_database,
    retry_on_database_error,
    Base
)

# Initialize the robust database connection
_database_initialized = False

def ensure_database_initialized():
    """Ensure database is initialized before use"""
    global _database_initialized
    if not _database_initialized:
        initialize_database()
        _database_initialized = True

# Backwards compatibility - these will use the robust manager
def get_engine():
    """Get database engine with automatic initialization"""
    ensure_database_initialized()
    return db_manager.engine

def get_session_local():
    """Get session factory with automatic initialization"""
    ensure_database_initialized()
    return db_manager.SessionLocal

# Legacy support - create engine and session for existing code
ensure_database_initialized()
sync_engine = get_engine()
SessionLocal = get_session_local()

# Export the robust get_db function
__all__ = ['get_db', 'Base', 'sync_engine', 'SessionLocal', 'retry_on_database_error']
