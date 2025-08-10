"""
TTPROv5 Configuration Settings
Secure configuration with environment variable validation
"""
import os
import logging
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )
    
    # Core Application
    APP_NAME: str = "TitleTesterPro"
    ENVIRONMENT: str = "production"
    LOG_LEVEL: str = "info"
    DEBUG: bool = False
    
    # Database
    DATABASE_URL: str
    
    # Redis
    REDIS_URL: str
    
    # Firebase Admin (SECRET_FILE only)
    GOOGLE_APPLICATION_CREDENTIALS: str = "/etc/secrets/firebase-key.json"
    ALLOW_ENV_FALLBACK: str = "0"
    FIREBASE_DEBUG: str = "0"
    
    # Google OAuth (Backend Web Client)
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_API_KEY: str
    
    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS Origins
    CORS_ORIGINS: str = "https://www.titletesterpro.com,https://titletesterpro.com"
    
    # Session Settings
    SESSION_COOKIE_NAME: str = "ttpro_session"
    SESSION_MAX_AGE: int = 86400  # 24 hours
    
    # Optional Stripe
    STRIPE_SECRET_KEY: str = ""
    STRIPE_PUBLISHABLE_KEY: str = ""
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins into list"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]
    
    @property
    def is_debug_mode(self) -> bool:
        """Check if Firebase debug mode is enabled"""
        return self.FIREBASE_DEBUG == "1"
    
    def validate_firebase_config(self) -> bool:
        """Validate Firebase configuration"""
        try:
            # Check if secret file exists
            if os.path.exists(self.GOOGLE_APPLICATION_CREDENTIALS):
                logger.info(f"✅ Firebase secret file found: {self.GOOGLE_APPLICATION_CREDENTIALS}")
                return True
            else:
                logger.error(f"❌ Firebase secret file not found: {self.GOOGLE_APPLICATION_CREDENTIALS}")
                return False
        except Exception as e:
            logger.error(f"❌ Firebase config validation failed: {e}")
            return False

# Global settings instance
settings = Settings()

def setup_logging():
    """Configure application logging"""
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Suppress noisy third-party logs in production
    if settings.ENVIRONMENT == "production":
        logging.getLogger("httpx").setLevel(logging.WARNING)
        logging.getLogger("httpcore").setLevel(logging.WARNING)
        logging.getLogger("urllib3").setLevel(logging.WARNING)

# Setup logging when module is imported
setup_logging()