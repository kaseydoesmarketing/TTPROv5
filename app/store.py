"""
TTPROv5 Data Store Layer
Database and Redis connections with session management
"""
import json
import logging
from typing import Optional, Dict, Any, List
import redis
import asyncpg
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from .settings import settings

logger = logging.getLogger(__name__)

class RedisStore:
    """Redis connection and session management"""
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.connect()
    
    def connect(self):
        """Initialize Redis connection"""
        try:
            self.redis_client = redis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30
            )
            # Test connection
            self.redis_client.ping()
            logger.info("✅ Redis connected successfully")
        except Exception as e:
            logger.error(f"❌ Redis connection failed: {e}")
            self.redis_client = None
    
    def is_connected(self) -> bool:
        """Check if Redis is connected"""
        try:
            return self.redis_client is not None and self.redis_client.ping()
        except:
            return False
    
    def set_session(self, session_id: str, user_data: Dict[str, Any], expire_seconds: int = 86400):
        """Store user session in Redis"""
        if not self.redis_client:
            logger.error("❌ Redis not connected - cannot set session")
            return False
        
        try:
            session_key = f"session:{session_id}"
            self.redis_client.setex(
                session_key,
                expire_seconds,
                json.dumps(user_data)
            )
            logger.info(f"✅ Session stored: {session_id[:8]}...")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to set session: {e}")
            return False
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve user session from Redis"""
        if not self.redis_client:
            logger.error("❌ Redis not connected - cannot get session")
            return None
        
        try:
            session_key = f"session:{session_id}"
            session_data = self.redis_client.get(session_key)
            
            if session_data:
                return json.loads(session_data)
            return None
        except Exception as e:
            logger.error(f"❌ Failed to get session: {e}")
            return None
    
    def delete_session(self, session_id: str) -> bool:
        """Delete user session from Redis"""
        if not self.redis_client:
            logger.error("❌ Redis not connected - cannot delete session")
            return False
        
        try:
            session_key = f"session:{session_id}"
            result = self.redis_client.delete(session_key)
            logger.info(f"✅ Session deleted: {session_id[:8]}...")
            return result > 0
        except Exception as e:
            logger.error(f"❌ Failed to delete session: {e}")
            return False
    
    def extend_session(self, session_id: str, expire_seconds: int = 86400) -> bool:
        """Extend session expiry"""
        if not self.redis_client:
            return False
        
        try:
            session_key = f"session:{session_id}"
            return self.redis_client.expire(session_key, expire_seconds)
        except Exception as e:
            logger.error(f"❌ Failed to extend session: {e}")
            return False

class DatabaseStore:
    """PostgreSQL database connection and operations"""
    
    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self.connect()
    
    def connect(self):
        """Initialize database connection"""
        try:
            self.engine = create_engine(
                settings.DATABASE_URL,
                pool_size=10,
                max_overflow=20,
                pool_pre_ping=True,
                pool_recycle=3600
            )
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            # Test connection
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT 1")).scalar()
                if result == 1:
                    logger.info("✅ Database connected successfully")
                else:
                    raise Exception("Database health check failed")
                    
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            self.engine = None
            self.SessionLocal = None
    
    def is_connected(self) -> bool:
        """Check if database is connected"""
        try:
            if not self.engine:
                return False
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1")).scalar()
                return True
        except:
            return False
    
    def get_session(self) -> Optional[Session]:
        """Get database session"""
        if not self.SessionLocal:
            logger.error("❌ Database not connected - cannot create session")
            return None
        
        try:
            return self.SessionLocal()
        except Exception as e:
            logger.error(f"❌ Failed to create database session: {e}")
            return None
    
    def execute_query(self, query: str, params: Optional[Dict] = None) -> Optional[List]:
        """Execute raw SQL query"""
        if not self.engine:
            logger.error("❌ Database not connected - cannot execute query")
            return None
        
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(query), params or {})
                return result.fetchall()
        except Exception as e:
            logger.error(f"❌ Query execution failed: {e}")
            return None

# Global store instances
redis_store = RedisStore()
database_store = DatabaseStore()

def get_redis() -> RedisStore:
    """Get Redis store instance"""
    return redis_store

def get_database() -> DatabaseStore:
    """Get database store instance"""
    return database_store

def health_check() -> Dict[str, Any]:
    """Check health of all store connections"""
    return {
        "redis": {
            "connected": redis_store.is_connected(),
            "url_configured": bool(settings.REDIS_URL)
        },
        "database": {
            "connected": database_store.is_connected(),
            "url_configured": bool(settings.DATABASE_URL)
        }
    }