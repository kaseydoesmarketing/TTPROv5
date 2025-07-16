from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    database_url: str = "sqlite:///./titletesterpro.db"
    
    redis_url: str = "redis://localhost:6379"
    
    firebase_project_id: str = "dev-project"
    firebase_private_key_id: str = "dev-key-id"
    firebase_private_key: str = "dev-private-key"
    firebase_client_email: str = "dev@example.com"
    firebase_client_id: str = "dev-client-id"
    firebase_auth_uri: str = "https://accounts.google.com/o/oauth2/auth"
    firebase_token_uri: str = "https://oauth2.googleapis.com/token"
    
    google_client_id: str = "dev-google-client-id"
    google_client_secret: str = "dev-google-client-secret"
    
    youtube_api_key: str = "dev-youtube-api-key"
    
    secret_key: str = "dev-secret-key-change-in-production"
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:5173", "http://localhost:5174"]
    environment: str = "development"
    
    class Config:
        env_file = ".env"


settings = Settings()
