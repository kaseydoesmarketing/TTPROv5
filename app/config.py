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
    
    # Firebase Configuration (with Railway-compatible defaults)
    firebase_project_id: str = "titletesterpro"
    firebase_private_key_id: str = "emergency-fallback-key"
    firebase_private_key: str = "-----BEGIN PRIVATE KEY-----\nEMERGENCY_FALLBACK_KEY\n-----END PRIVATE KEY-----"
    firebase_client_email: str = "firebase-adminsdk@titletesterpro.iam.gserviceaccount.com"
    firebase_client_id: str = "100000000000000000000"
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
    cors_origins: str = "http://localhost:3000,http://localhost:5173,http://localhost:5174,https://www.titletesterpro.com,https://titletesterpro.com"
    environment: str = "production"
    
    log_level: str = "INFO"
    
    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    @property
    def is_development(self) -> bool:
        return self.environment.lower() in ["development", "dev", "local"]
    
    @property
    def is_production(self) -> bool:
        return self.environment.lower() in ["production", "prod"]
    
    def get_firebase_service_account_dict(self) -> dict:
        """Get Firebase service account configuration as dictionary"""
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
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
