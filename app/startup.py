"""
Crash-proof application startup and configuration
Handles all possible Railway deployment failures gracefully
"""

import logging
import os
import sys
from typing import Optional

from .middleware import validate_environment_at_startup, log_environment_status
from .env_validator import env_validator

logger = logging.getLogger(__name__)

class SafeStartup:
    def __init__(self):
        self.database_available = False
        self.redis_available = False
        self.firebase_available = False
        self.startup_errors = []
        self.environment_status = None
        
    def safe_database_init(self):
        """Initialize database with comprehensive error handling using robust manager"""
        try:
            from .database_manager import db_manager
            
            # Use the robust database manager
            success = db_manager.create_engine_with_retry()
            
            if success:
                # Test the connection and get status
                connection_status = db_manager.get_connection_status()
                
                if connection_status["healthy"]:
                    self.database_available = True
                    logger.info("✅ Database connection established with robust manager")
                    
                    # Log connection details
                    if connection_status["pool_info"]:
                        pool_info = connection_status["pool_info"]
                        logger.info(f"📊 Connection pool: {pool_info['checked_in']} available, {pool_info['checked_out']} in use")
                    
                    return True
                else:
                    self.startup_errors.append("Database connection unhealthy")
                    logger.error("❌ Database connection established but unhealthy")
                    return False
            else:
                self.startup_errors.append("Database manager initialization failed")
                logger.error("❌ Database manager initialization failed")
                return False
                
        except Exception as e:
            self.startup_errors.append(f"Database initialization error: {str(e)}")
            logger.error(f"❌ Database init failed: {e}")
            return False
    
    def safe_redis_init(self):
        """Initialize Redis and job manager with error handling - Railway deployment safe"""
        try:
            # Check if this is a Railway deployment - skip Redis if so
            import os
            if os.getenv('RAILWAY_ENVIRONMENT') or os.getenv('RAILWAY_PROJECT_ID'):
                logger.info("ℹ️ Railway deployment detected - skipping Redis initialization")
                return False
                
            from .config import settings
            redis_url = getattr(settings, 'redis_url', None)
            
            if not redis_url or redis_url == "redis://localhost:6379/0":
                logger.info("ℹ️ Using fallback Redis URL - skipping in deployment")
                return False
                
            # Test basic Redis connection with short timeout
            import redis
            r = redis.from_url(redis_url, socket_timeout=2, socket_connect_timeout=2)
            r.ping()
            
            # Initialize the robust job manager only if Redis works
            from .job_manager import RobustJobManager
            job_manager = RobustJobManager()
            self.redis_available = True
            logger.info("✅ Redis and job manager initialized successfully")
            return True
            
        except Exception as e:
            # Don't log as error - this is expected in Railway deployment
            logger.info(f"ℹ️ Redis unavailable (expected in deployment): {e}")
            logger.info("ℹ️ Background jobs will be disabled - application will continue")
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
        # Determine overall status based on environment and services
        if self.environment_status and not self.environment_status.get("startup_safe", False):
            overall_status = "emergency"
        elif self.firebase_available and self.database_available:
            overall_status = "healthy"
        elif self.firebase_available:
            overall_status = "degraded"
        else:
            overall_status = "emergency"
            
        return {
            "database_available": self.database_available,
            "redis_available": self.redis_available, 
            "firebase_available": self.firebase_available,
            "environment_status": self.environment_status.get("mode", "unknown") if self.environment_status else "unknown",
            "environment_safe": self.environment_status.get("startup_safe", False) if self.environment_status else False,
            "errors": self.startup_errors,
            "status": overall_status
        }

# Global startup manager
startup_manager = SafeStartup()

def run_startup_checks():
    """Initialize application with comprehensive error handling"""
    logger.info("🚀 Starting TitleTesterPro backend...")
    
    # First, validate environment variables
    try:
        startup_manager.environment_status = validate_environment_at_startup()
        log_environment_status()
        
        # Add environment errors to startup errors
        if not startup_manager.environment_status["startup_safe"]:
            startup_manager.startup_errors.append("Environment validation failed")
            
    except Exception as e:
        logger.error(f"❌ Environment validation failed: {e}")
        startup_manager.startup_errors.append(f"Environment validation error: {str(e)}")
        startup_manager.environment_status = {
            "startup_safe": False,
            "mode": "emergency",
            "error": str(e)
        }
    
    # Only proceed with service initialization if environment is valid
    if startup_manager.environment_status.get("startup_safe", False):
        # Try to initialize each service
        startup_manager.safe_database_init()
        startup_manager.safe_redis_init()
        startup_manager.safe_firebase_init()
    else:
        logger.warning("⚠️ Skipping service initialization due to environment issues")
    
    status = startup_manager.get_startup_status()
    
    if status["status"] == "healthy":
        logger.info("✅ Application startup completed successfully")
    else:
        logger.warning("⚠️ Application started in degraded mode")
        for error in status["errors"]:
            logger.warning(f"   - {error}")
    
    return status