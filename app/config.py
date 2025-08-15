from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
	# Database and Redis
	database_url: str = os.getenv("DATABASE_URL", "sqlite:///./titletesterpro.db")
	redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
	
	# Google OAuth (for YouTube)
	google_client_id: str = os.getenv("GOOGLE_OAUTH_CLIENT_ID", "")
	google_client_secret: str = os.getenv("GOOGLE_OAUTH_CLIENT_SECRET", "")
	
	# YouTube API (optional)
	youtube_api_key: Optional[str] = os.getenv("YOUTUBE_API_KEY")
	
	# Application secret
	secret_key: str = os.getenv("SECRET_KEY", "change-me-in-prod")
	# Webhook HMAC secret for Auth0 Actions -> our backend
	auth0_action_hmac_secret: Optional[str] = os.getenv("AUTH0_ACTION_HMAC_SECRET")
	
	# Stripe Configuration (Optional)
	stripe_secret_key: Optional[str] = os.getenv("STRIPE_SECRET_KEY")
	stripe_publishable_key: Optional[str] = os.getenv("STRIPE_PUBLISHABLE_KEY")
	stripe_webhook_secret: Optional[str] = os.getenv("STRIPE_WEBHOOK_SECRET")
	environment: str = os.getenv("ENV", "production")
	
	log_level: str = os.getenv("LOG_LEVEL", "INFO")
	
	@property
	def is_development(self) -> bool:
		return self.environment.lower() in ["development", "dev", "local"]
	
	@property
	def is_production(self) -> bool:
		return self.environment.lower() in ["production", "prod"]
	
	class Config:
		env_file = ".env"
		case_sensitive = False


settings = Settings()
