"""
Crash-proof application startup and configuration
Handles all possible Railway deployment failures gracefully
"""

import logging
import os
import sys
from typing import Optional

logger = logging.getLogger(__name__)

class SafeStartup:
    def __init__(self):
        self.database_available = False
        self.redis_available = False
        self.firebase_available = False
        self.startup_errors = []
        
    def safe_database_init(self):
        """Initialize database with comprehensive error handling"""
        try:
            from .config import settings
            database_url = getattr(settings, 'database_url', None)
            
            if not database_url:
                self.startup_errors.append("DATABASE_URL not configured")
                logger.warning("⚠️ DATABASE_URL not set, using in-memory fallback")
                return False
                
            # Test basic connection
            if database_url.startswith('postgresql'):
                try:
                    import psycopg2
                    from urllib.parse import urlparse
                    
                    parsed = urlparse(database_url)
                    conn = psycopg2.connect(
                        host=parsed.hostname,
                        port=parsed.port or 5432,
                        database=parsed.path.lstrip('/'),
                        user=parsed.username,
                        password=parsed.password,
                        connect_timeout=5
                    )
                    conn.close()
                    self.database_available = True
                    logger.info("✅ PostgreSQL connection successful")
                    return True
                    
                except Exception as e:
                    self.startup_errors.append(f"PostgreSQL connection failed: {str(e)}")
                    logger.error(f"❌ PostgreSQL failed: {e}")
                    return False
            else:
                # SQLite or other database
                self.database_available = True
                logger.info("✅ Database fallback configured")
                return True
                
        except Exception as e:
            self.startup_errors.append(f"Database initialization error: {str(e)}")
            logger.error(f"❌ Database init failed: {e}")
            return False
    
    def safe_redis_init(self):
        """Initialize Redis with error handling"""
        try:
            from .config import settings
            redis_url = getattr(settings, 'redis_url', None)
            
            if not redis_url:
                self.startup_errors.append("REDIS_URL not configured")
                logger.warning("⚠️ REDIS_URL not set, using in-memory cache")
                return False
                
            # Test Redis connection
            import redis
            r = redis.from_url(redis_url, socket_timeout=5)
            r.ping()
            self.redis_available = True
            logger.info("✅ Redis connection successful")
            return True
            
        except Exception as e:
            self.startup_errors.append(f"Redis connection failed: {str(e)}")
            logger.error(f"❌ Redis failed: {e}")
            return False
    
    def safe_firebase_init(self):
        """Initialize Firebase with error handling"""
        try:
            from .firebase_auth import initialize_firebase
            initialize_firebase()
            self.firebase_available = True
            logger.info("✅ Firebase initialized")
            return True
            
        except Exception as e:
            self.startup_errors.append(f"Firebase initialization failed: {str(e)}")
            logger.error(f"❌ Firebase failed: {e}")
            return False
    
    def get_startup_status(self):
        """Get comprehensive startup status"""
        return {
            "database_available": self.database_available,
            "redis_available": self.redis_available, 
            "firebase_available": self.firebase_available,
            "errors": self.startup_errors,
            "status": "healthy" if self.firebase_available else "degraded"
        }

# Global startup manager
startup_manager = SafeStartup()

def run_startup_checks():
    """Initialize application with comprehensive error handling"""
    logger.info("🚀 Starting TitleTesterPro backend...")
    
    # Try to initialize each service
    startup_manager.safe_database_init()
    startup_manager.safe_redis_init()
    startup_manager.safe_firebase_init()
    
    status = startup_manager.get_startup_status()
    
    if status["status"] == "healthy":
        logger.info("✅ Application startup completed successfully")
    else:
        logger.warning("⚠️ Application started in degraded mode")
        for error in status["errors"]:
            logger.warning(f"   - {error}")
    
    return status