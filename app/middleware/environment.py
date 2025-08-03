"""
Environment validation middleware
Ensures application doesn't start with invalid configuration
"""

import logging
import os
import sys
from typing import Dict, List
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from ..env_validator import env_validator

logger = logging.getLogger(__name__)

class EnvironmentValidationMiddleware(BaseHTTPMiddleware):
    """Middleware that validates environment variables and prevents unsafe startup"""
    
    def __init__(self, app, enforce_critical: bool = True):
        super().__init__(app)
        self.enforce_critical = enforce_critical
        self.validation_performed = False
        self.startup_safe = False
        
    async def dispatch(self, request: Request, call_next):
        # Only validate once during startup
        if not self.validation_performed:
            self.validate_startup_environment()
            self.validation_performed = True
        
        # If critical validation failed and enforcement is enabled, block all requests except health checks
        if self.enforce_critical and not self.startup_safe:
            if request.url.path not in ["/health", "/health-detailed", "/healthz", "/"]:
                return JSONResponse(
                    status_code=503,
                    content={
                        "error": "Service unavailable due to configuration issues",
                        "message": "Critical environment variables are missing or invalid",
                        "check_endpoint": "/health",
                        "mode": "emergency"
                    }
                )
        
        response = await call_next(request)
        return response
    
    def validate_startup_environment(self):
        """Validate environment and determine if startup is safe"""
        logger.info("🔍 Running environment validation middleware...")
        
        try:
            validation_results = env_validator.validate_all()
            summary = env_validator.get_status_summary()
            
            self.startup_safe = summary["can_start"]
            
            if summary["mode"] == "emergency":
                logger.error("🚨 EMERGENCY: Application cannot start safely")
                logger.error("Missing critical environment variables - check configuration")
                if self.enforce_critical:
                    logger.error("All non-health endpoints will return 503")
            elif summary["mode"] == "degraded":
                logger.warning("⚠️ DEGRADED: Application starting with reduced functionality")
                self.startup_safe = True  # Allow degraded startup
            else:
                logger.info("✅ Environment validation passed - normal startup")
                self.startup_safe = True
                
        except Exception as e:
            logger.error(f"❌ Environment validation failed: {e}")
            self.startup_safe = False

def create_environment_validation_middleware(enforce_critical: bool = True):
    """Factory function to create environment validation middleware"""
    return lambda app: EnvironmentValidationMiddleware(app, enforce_critical=enforce_critical)

def validate_environment_at_startup() -> Dict:
    """Standalone function to validate environment during startup"""
    logger.info("🔍 Validating environment variables at startup...")
    
    try:
        validation_results = env_validator.validate_all()
        summary = env_validator.get_status_summary()
        
        # Log startup decision
        if summary["mode"] == "emergency":
            logger.error("🚨 CRITICAL FAILURE: Cannot start with missing critical variables")
            logger.error("Application will run in emergency mode with limited functionality")
        elif summary["mode"] == "degraded":
            logger.warning("⚠️ DEGRADED START: Some features may not work properly")
        else:
            logger.info("✅ All environment checks passed - starting normally")
        
        return {
            "startup_safe": summary["can_start"],
            "mode": summary["mode"],
            "validation_results": validation_results,
            "summary": summary
        }
        
    except Exception as e:
        logger.error(f"❌ Environment validation error: {e}")
        return {
            "startup_safe": False,
            "mode": "emergency",
            "validation_results": {},
            "summary": {"error": str(e)},
            "exception": str(e)
        }

def check_critical_env_vars() -> bool:
    """Quick check for critical environment variables only"""
    critical_vars = [
        "FIREBASE_PROJECT_ID",
        "FIREBASE_PRIVATE_KEY",
        "FIREBASE_CLIENT_EMAIL",
        "GOOGLE_CLIENT_ID", 
        "GOOGLE_CLIENT_SECRET",
        "YOUTUBE_API_KEY",
        "SECRET_KEY"
    ]
    
    missing = []
    for var in critical_vars:
        if not os.environ.get(var):
            missing.append(var)
    
    if missing:
        logger.error(f"❌ Missing critical environment variables: {', '.join(missing)}")
        return False
    
    logger.info("✅ All critical environment variables present")
    return True

def log_environment_status():
    """Log current environment status for debugging"""
    logger.info("📊 Environment Status Report:")
    summary = env_validator.get_status_summary()
    
    logger.info(f"   Mode: {summary['mode']}")
    logger.info(f"   Configured: {summary['present']}/{summary['total_vars']} variables")
    logger.info(f"   Missing Critical: {summary['missing_critical']}")
    logger.info(f"   Missing Important: {summary['missing_important']}")
    logger.info(f"   Can Start: {summary['can_start']}")
    
    if summary["mode"] != "normal":
        logger.warning("⚠️ See /health endpoint for detailed status")