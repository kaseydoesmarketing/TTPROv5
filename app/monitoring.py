"""
Comprehensive System Monitoring and Alerting
Monitors all application components and provides health insights
"""

import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

from .env_validator import env_validator
from .database_manager import db_manager
from .job_manager import job_manager
from .auth_manager import auth_manager
from .youtube_quota_manager import youtube_quota_manager
from .stripe_webhook_manager import stripe_webhook_manager

logger = logging.getLogger(__name__)

class SystemMonitor:
    """Comprehensive system monitoring"""
    
    def __init__(self):
        self.last_check = None
        self.check_interval = 30  # seconds
        
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        try:
            current_time = datetime.utcnow()
            
            # Environment status
            env_status = env_validator.get_health_check_data()
            
            # Database status  
            db_status = db_manager.get_connection_status()
            
            # Job queue status
            job_status = job_manager.get_health_status()
            
            # Authentication status
            auth_status = auth_manager.get_auth_status()
            
            # YouTube API status
            yt_status = youtube_quota_manager.get_quota_status()
            
            # Stripe status
            stripe_status = stripe_webhook_manager.get_webhook_health()
            
            # Overall system health
            all_healthy = all([
                env_status.get("can_start", False),
                db_status.get("healthy", False),
                job_status.get("redis_connected", False),
                auth_status.get("firebase_initialized", False)
            ])
            
            overall_status = "healthy" if all_healthy else "degraded"
            
            return {
                "timestamp": current_time.isoformat(),
                "overall_status": overall_status,
                "components": {
                    "environment": {
                        "status": env_status.get("environment_status", "unknown"),
                        "can_start": env_status.get("can_start", False),
                        "missing_critical": env_status.get("missing_critical", 0)
                    },
                    "database": {
                        "status": "healthy" if db_status.get("healthy", False) else "unhealthy",
                        "connection_pool": db_status.get("pool_info", {}),
                        "type": db_status.get("database_url_type", "unknown")
                    },
                    "job_queue": {
                        "status": job_status.get("status", "unknown"),
                        "redis_connected": job_status.get("redis_connected", False),
                        "statistics": job_status.get("statistics", {})
                    },
                    "authentication": {
                        "status": "healthy" if auth_status.get("firebase_initialized", False) else "degraded",
                        "firebase_initialized": auth_status.get("firebase_initialized", False),
                        "jwks_cached": auth_status.get("jwks_cached", False)
                    },
                    "youtube_api": {
                        "status": yt_status.get("status", "unknown"),
                        "daily_quota": yt_status.get("daily", {}),
                        "rate_limits": yt_status.get("rate_limit_100s", {})
                    },
                    "stripe": {
                        "status": "healthy" if stripe_status.get("initialized", False) else "degraded",
                        "configured": stripe_status.get("stripe_configured", False),
                        "webhook_ready": stripe_status.get("webhook_secret_configured", False)
                    }
                },
                "uptime_checks": {
                    "can_process_requests": all_healthy,
                    "can_handle_auth": auth_status.get("firebase_initialized", False),
                    "can_process_jobs": job_status.get("redis_connected", False),
                    "can_call_youtube_api": yt_status.get("daily", {}).get("remaining", 0) > 0
                }
            }
            
        except Exception as e:
            logger.error(f"❌ System monitoring failed: {e}")
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "overall_status": "error",
                "error": str(e)
            }

# Global monitor instance
system_monitor = SystemMonitor()