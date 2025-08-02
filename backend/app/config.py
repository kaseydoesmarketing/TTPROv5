from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    database_url: str
    redis_url: str
    
    firebase_project_id: str
    firebase_private_key_id: str
    firebase_private_key: str
    firebase_client_email: str
    firebase_client_id: str
    firebase_auth_uri: str = "https://accounts.google.com/o/oauth2/auth"
    firebase_token_uri: str = "https://oauth2.googleapis.com/token"
    firebase_auth_provider_x509_cert_url: str = "https://www.googleapis.com/oauth2/v1/certs"
    firebase_client_x509_cert_url: Optional[str] = None
    
    google_client_id: str
    google_client_secret: str
    
    youtube_api_key: str
    
    secret_key: str
    cors_origins: List[str] = [
        "http://localhost:3000", 
        "http://localhost:5173", 
        "http://localhost:5174",
        "https://ttprov4.vercel.app",
        "https://titletesterpro.com"
    ]
    environment: str = "production"
    
    log_level: str = "INFO"
    
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
