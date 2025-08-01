import time
from datetime import datetime, timedelta
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from ..database import SessionLocal
from ..models import User
import logging
from ..config import settings

logger = logging.getLogger(__name__)

def refresh_google_token(user: User) -> str:
    """Refresh Google OAuth tokens using stored refresh token"""
    try:
        logger.info(f"Refreshing token for user {user.id}")
        
        refresh_token = user.get_google_refresh_token()
        if not refresh_token:
            raise ValueError("No refresh token available")
        
        creds = Credentials(
            token=None,
            refresh_token=refresh_token,
            client_id=settings.google_client_id,
            client_secret=settings.google_client_secret,
            token_uri="https://oauth2.googleapis.com/token"
        )
        
        creds.refresh(Request())
        
        db = SessionLocal()
        try:
            expires_in = int(creds.expiry.timestamp() - time.time()) if creds.expiry else 3600
            
            user.set_google_tokens(
                access_token=creds.token,
                refresh_token=creds.refresh_token or refresh_token,  # Keep existing if new one not provided
                expires_in=expires_in
            )
            
            db.add(user)
            db.commit()
            logger.info(f"Token refreshed for user {user.id}")
            return creds.token
        finally:
            db.close()
        
    except Exception as e:
        logger.error(f"Token refresh failed: {str(e)}")
        raise ValueError("Token refresh failed. Please re-authenticate.")
