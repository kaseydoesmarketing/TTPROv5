import logging
import requests
from typing import Optional
from .config import settings
from .models import User
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

async def refresh_google_access_token(user: User, db: Session) -> Optional[str]:
    """
    Refresh Google access token using refresh token
    
    Args:
        user: User object with encrypted refresh token
        db: Database session for updating user tokens
        
    Returns:
        New access token if successful, None if failed
    """
    refresh_token = user.get_google_refresh_token()
    if not refresh_token:
        logger.error(f"No refresh token available for user {user.id}")
        return None
    
    try:
        token_url = "https://oauth2.googleapis.com/token"
        token_data = {
            "client_id": settings.google_client_id,
            "client_secret": settings.google_client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        }
        
        logger.info(f"Attempting to refresh access token for user {user.id}")
        response = requests.post(token_url, data=token_data)
        
        if not response.ok:
            logger.error(f"Token refresh failed for user {user.id}: {response.status_code} - {response.text}")
            return None
        
        token_json = response.json()
        new_access_token = token_json.get("access_token")
        expires_in = token_json.get("expires_in", 3600)
        
        if new_access_token:
            user.set_google_tokens(
                access_token=new_access_token,
                refresh_token=refresh_token,  # Keep existing refresh token
                expires_in=expires_in
            )
            db.commit()
            logger.info(f"Successfully refreshed access token for user {user.id}, expires in {expires_in} seconds")
            return new_access_token
        else:
            logger.error(f"No access token in refresh response for user {user.id}")
            return None
        
    except requests.RequestException as e:
        logger.error(f"Network error refreshing access token for user {user.id}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error refreshing access token for user {user.id}: {e}")
        return None
