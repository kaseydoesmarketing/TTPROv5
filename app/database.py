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
	initialize_database,
	retry_on_database_error,
	Base
)
from typing import Generator

# Initialize the robust database connection
_database_initialized = False

def ensure_database_initialized() -> None:
	"""Ensure database is initialized before use"""
	global _database_initialized
	if not _database_initialized:
		initialize_database()
		_database_initialized = True

# Public dependency that guarantees initialization

def get_db() -> Generator:
	"""FastAPI dependency that ensures DB initialization before yielding a session."""
	ensure_database_initialized()
	session = db_manager.get_session_with_retry()
	if not session:
		raise RuntimeError("Database session unavailable")
	try:
		yield session
	finally:
		session.close()

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
# Note: Removed automatic initialization to prevent startup crashes
# Database will be initialized on first use instead
sync_engine = None
SessionLocal = None

__all__ = ['get_db', 'Base', 'sync_engine', 'SessionLocal', 'retry_on_database_error']
