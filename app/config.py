from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    # Railway provides DATABASE_URL and REDIS_URL automatically when you provision these services
    # If not set, fallback to SQLite for development
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./titletesterpro.db")
    
    # Railway provides REDIS_URL when you add Redis service
    # If not set, fallback to local Redis URL
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # Firebase Configuration - SECURE METHOD (Render Secret File)
    # Preferred: Set GOOGLE_APPLICATION_CREDENTIALS=/opt/render/project/secrets/service-account.json
    # This points to a Render Secret File containing the complete Firebase service account JSON
    
    # Firebase Configuration - FALLBACK METHOD (Environment Variables)
    # Only used if GOOGLE_APPLICATION_CREDENTIALS is not set
    firebase_project_id: str = os.getenv("FIREBASE_PROJECT_ID", "titletesterpro")
    firebase_private_key_id: str = os.getenv("FIREBASE_PRIVATE_KEY_ID", "emergency-fallback-key")
    firebase_private_key: str = os.getenv("FIREBASE_PRIVATE_KEY", "-----BEGIN PRIVATE KEY-----\nEMERGENCY_FALLBACK_KEY\n-----END PRIVATE KEY-----")
    firebase_client_email: str = os.getenv("FIREBASE_CLIENT_EMAIL", "firebase-adminsdk@titletesterpro.iam.gserviceaccount.com")
    firebase_client_id: str = os.getenv("FIREBASE_CLIENT_ID", "100000000000000000000")
    firebase_auth_uri: str = "https://accounts.google.com/o/oauth2/auth"
    firebase_token_uri: str = "https://oauth2.googleapis.com/token"
    firebase_auth_provider_x509_cert_url: str = "https://www.googleapis.com/oauth2/v1/certs"
    firebase_client_x509_cert_url: Optional[str] = None
    
    # Google OAuth Configuration (with Railway-compatible defaults)
    google_client_id: str = "emergency-fallback-client-id"
    google_client_secret: str = "emergency-fallback-secret"
    
    # YouTube API Configuration (with Railway-compatible default)
    youtube_api_key: str = "emergency-fallback-api-key"
    
    # Application secret (with Railway-compatible default)
    secret_key: str = "emergency-fallback-secret-key-for-railway-deployment"
    
    # Stripe Configuration (Optional)
    stripe_secret_key: Optional[str] = None
    stripe_publishable_key: Optional[str] = None
    stripe_webhook_secret: Optional[str] = None
    environment: str = "production"
    
    log_level: str = "INFO"
    
    @property
    def is_development(self) -> bool:
        return self.environment.lower() in ["development", "dev", "local"]
    
    @property
    def is_production(self) -> bool:
        return self.environment.lower() in ["production", "prod"]
    
    def get_firebase_service_account_dict(self) -> dict:
        """Get Firebase service account configuration as dictionary (FALLBACK ONLY)
        
        ⚠️ WARNING: This method should only be used when GOOGLE_APPLICATION_CREDENTIALS is not available.
        The preferred method is to use a Render Secret File pointed to by GOOGLE_APPLICATION_CREDENTIALS.
        """
        return {
            "type": "service_account",
            "project_id": self.firebase_project_id,
            "private_key_id": self.firebase_private_key_id,
            "private_key": self.firebase_private_key.replace('\\n', '\n'),
            "client_email": self.firebase_client_email,
            "client_id": self.firebase_client_id,
            "auth_uri": self.firebase_auth_uri,
            "token_uri": self.firebase_token_uri,
            "auth_provider_x509_cert_url": self.firebase_auth_provider_x509_cert_url,
            "client_x509_cert_url": self.firebase_client_x509_cert_url or f"https://www.googleapis.com/robot/v1/metadata/x509/{self.firebase_client_email}"
        }
    
    @property
    def is_using_secure_firebase_config(self) -> bool:
        """Check if using secure Firebase configuration (service account file)"""
        return bool(os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
