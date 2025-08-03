"""
Environment Variable Validation and Monitoring
Ensures all critical environment variables are present and valid
"""

import os
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)

class EnvVarStatus(Enum):
    PRESENT = "present"
    MISSING = "missing"
    INVALID = "invalid"
    EMPTY = "empty"

class EnvVarCategory(Enum):
    CRITICAL = "critical"  # App won't start without these
    IMPORTANT = "important"  # App degrades without these
    OPTIONAL = "optional"  # Nice to have

class EnvironmentValidator:
    """Validates and monitors environment variables"""
    
    # Define all environment variables with their categories and validation rules
    ENV_VAR_DEFINITIONS = {
        # Database
        "DATABASE_URL": {
            "category": EnvVarCategory.CRITICAL,
            "description": "PostgreSQL connection string",
            "validator": lambda x: x.startswith(("postgresql://", "postgres://", "sqlite://")),
            "fallback": "sqlite:///./titletesterpro.db",
            "sensitive": True
        },
        
        # Redis
        "REDIS_URL": {
            "category": EnvVarCategory.IMPORTANT,
            "description": "Redis connection string for job queue",
            "validator": lambda x: x.startswith(("redis://", "rediss://")),
            "fallback": "redis://localhost:6379/0",
            "sensitive": True
        },
        
        # Firebase
        "FIREBASE_PROJECT_ID": {
            "category": EnvVarCategory.CRITICAL,
            "description": "Firebase project identifier",
            "validator": lambda x: len(x) > 0,
            "sensitive": False
        },
        "FIREBASE_PRIVATE_KEY": {
            "category": EnvVarCategory.CRITICAL,
            "description": "Firebase service account private key",
            "validator": lambda x: "BEGIN PRIVATE KEY" in x or "BEGIN RSA PRIVATE KEY" in x,
            "sensitive": True
        },
        "FIREBASE_PRIVATE_KEY_ID": {
            "category": EnvVarCategory.CRITICAL,
            "description": "Firebase private key ID",
            "validator": lambda x: len(x) > 0,
            "sensitive": False
        },
        "FIREBASE_CLIENT_EMAIL": {
            "category": EnvVarCategory.CRITICAL,
            "description": "Firebase service account email",
            "validator": lambda x: "@" in x and x.endswith(".iam.gserviceaccount.com"),
            "sensitive": False
        },
        "FIREBASE_CLIENT_ID": {
            "category": EnvVarCategory.CRITICAL,
            "description": "Firebase client ID",
            "validator": lambda x: x.isdigit() and len(x) > 10,
            "sensitive": False
        },
        
        # Google OAuth
        "GOOGLE_CLIENT_ID": {
            "category": EnvVarCategory.CRITICAL,
            "description": "Google OAuth client ID",
            "validator": lambda x: x.endswith(".apps.googleusercontent.com"),
            "sensitive": False
        },
        "GOOGLE_CLIENT_SECRET": {
            "category": EnvVarCategory.CRITICAL,
            "description": "Google OAuth client secret",
            "validator": lambda x: len(x) > 10,
            "sensitive": True
        },
        
        # YouTube API
        "YOUTUBE_API_KEY": {
            "category": EnvVarCategory.CRITICAL,
            "description": "YouTube Data API key",
            "validator": lambda x: len(x) > 20,
            "sensitive": True
        },
        
        # Application
        "SECRET_KEY": {
            "category": EnvVarCategory.CRITICAL,
            "description": "Application secret key for sessions",
            "validator": lambda x: len(x) >= 32,
            "sensitive": True
        },
        
        # Stripe (Optional)
        "STRIPE_SECRET_KEY": {
            "category": EnvVarCategory.OPTIONAL,
            "description": "Stripe secret key for payments",
            "validator": lambda x: x.startswith(("sk_test_", "sk_live_")),
            "sensitive": True
        },
        "STRIPE_PUBLISHABLE_KEY": {
            "category": EnvVarCategory.OPTIONAL,
            "description": "Stripe publishable key",
            "validator": lambda x: x.startswith(("pk_test_", "pk_live_")),
            "sensitive": False
        },
        "STRIPE_WEBHOOK_SECRET": {
            "category": EnvVarCategory.OPTIONAL,
            "description": "Stripe webhook endpoint secret",
            "validator": lambda x: x.startswith("whsec_"),
            "sensitive": True
        },
        
        # Environment
        "ENVIRONMENT": {
            "category": EnvVarCategory.IMPORTANT,
            "description": "Application environment (production/development)",
            "validator": lambda x: x.lower() in ["production", "development", "staging", "test"],
            "fallback": "production",
            "sensitive": False
        },
        "CORS_ORIGINS": {
            "category": EnvVarCategory.IMPORTANT,
            "description": "Allowed CORS origins",
            "validator": lambda x: "http" in x,
            "fallback": "http://localhost:3000,http://localhost:5173",
            "sensitive": False
        }
    }
    
    def __init__(self):
        self.validation_results: Dict[str, Dict] = {}
        self.validation_timestamp: Optional[datetime] = None
        self.startup_mode: Optional[str] = None
        
    def validate_env_var(self, name: str, definition: Dict) -> Tuple[EnvVarStatus, Optional[str]]:
        """Validate a single environment variable"""
        value = os.environ.get(name)
        
        if not value:
            # Check for common variations
            variations = [
                name.lower(),
                name.upper(),
                name.replace("_", "-"),
                name.replace("-", "_")
            ]
            for variation in variations:
                value = os.environ.get(variation)
                if value:
                    logger.warning(f"Found {name} as {variation} - using this value")
                    break
        
        if not value:
            return EnvVarStatus.MISSING, "Environment variable not set"
        
        if value.strip() == "":
            return EnvVarStatus.EMPTY, "Environment variable is empty"
        
        # Run custom validator if provided
        if "validator" in definition:
            try:
                if not definition["validator"](value):
                    return EnvVarStatus.INVALID, "Failed validation check"
            except Exception as e:
                return EnvVarStatus.INVALID, f"Validation error: {str(e)}"
        
        return EnvVarStatus.PRESENT, None
    
    def validate_all(self) -> Dict[str, Dict]:
        """Validate all environment variables"""
        logger.info("Starting environment variable validation...")
        
        self.validation_results = {}
        critical_missing = []
        important_missing = []
        
        for var_name, definition in self.ENV_VAR_DEFINITIONS.items():
            status, error_msg = self.validate_env_var(var_name, definition)
            
            self.validation_results[var_name] = {
                "status": status.value,
                "category": definition["category"].value,
                "description": definition["description"],
                "error": error_msg,
                "has_fallback": "fallback" in definition
            }
            
            # Log based on severity
            if status != EnvVarStatus.PRESENT:
                if definition["category"] == EnvVarCategory.CRITICAL:
                    critical_missing.append(var_name)
                    logger.error(f"❌ CRITICAL: {var_name} - {error_msg}")
                elif definition["category"] == EnvVarCategory.IMPORTANT:
                    important_missing.append(var_name)
                    logger.warning(f"⚠️  IMPORTANT: {var_name} - {error_msg}")
                else:
                    logger.info(f"ℹ️  OPTIONAL: {var_name} - {error_msg}")
            else:
                logger.info(f"✅ {var_name} - Valid")
        
        self.validation_timestamp = datetime.utcnow()
        
        # Determine startup mode
        if critical_missing:
            self.startup_mode = "emergency"
            logger.error(f"🚨 EMERGENCY MODE: Missing critical env vars: {', '.join(critical_missing)}")
        elif important_missing:
            self.startup_mode = "degraded"
            logger.warning(f"⚠️  DEGRADED MODE: Missing important env vars: {', '.join(important_missing)}")
        else:
            self.startup_mode = "normal"
            logger.info("✅ All required environment variables present")
        
        return self.validation_results
    
    def get_safe_value(self, var_name: str) -> Optional[str]:
        """Get environment variable value with fallback"""
        definition = self.ENV_VAR_DEFINITIONS.get(var_name)
        if not definition:
            return os.environ.get(var_name)
        
        value = os.environ.get(var_name)
        if not value and "fallback" in definition:
            logger.warning(f"Using fallback value for {var_name}")
            return definition["fallback"]
        
        return value
    
    def get_status_summary(self) -> Dict:
        """Get a summary of environment validation status"""
        if not self.validation_results:
            self.validate_all()
        
        total = len(self.ENV_VAR_DEFINITIONS)
        present = sum(1 for r in self.validation_results.values() if r["status"] == "present")
        missing_critical = sum(1 for r in self.validation_results.values() 
                             if r["status"] != "present" and r["category"] == "critical")
        missing_important = sum(1 for r in self.validation_results.values() 
                              if r["status"] != "present" and r["category"] == "important")
        
        return {
            "timestamp": self.validation_timestamp.isoformat() if self.validation_timestamp else None,
            "mode": self.startup_mode,
            "total_vars": total,
            "present": present,
            "missing_critical": missing_critical,
            "missing_important": missing_important,
            "percentage_configured": (present / total * 100) if total > 0 else 0,
            "can_start": missing_critical == 0,
            "details": self.validation_results
        }
    
    def get_health_check_data(self) -> Dict:
        """Get environment health data for health endpoint"""
        summary = self.get_status_summary()
        
        # Remove sensitive details
        safe_details = {}
        for var_name, result in summary["details"].items():
            safe_details[var_name] = {
                "status": result["status"],
                "category": result["category"],
                "has_fallback": result.get("has_fallback", False)
            }
        
        return {
            "environment_status": summary["mode"],
            "can_start": summary["can_start"],
            "vars_configured": f"{summary['present']}/{summary['total_vars']}",
            "missing_critical": summary["missing_critical"],
            "last_check": summary["timestamp"]
        }

# Global validator instance
env_validator = EnvironmentValidator()