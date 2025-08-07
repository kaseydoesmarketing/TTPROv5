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
    logger.info(f"Starting token refresh for user {user.id} ({user.email})")
    
    try:
        user_id = user.id
        user_email = user.email
        logger.info(f"Refreshing token for user {user_id} ({user_email})")
        
        # Use completely separate session to avoid conflicts
        db = SessionLocal()
        try:
            # Get the user in this session to avoid session conflicts
            db_user = db.query(User).filter(User.id == user_id).first()
            if not db_user:
                logger.error(f"User {user_id} not found in database during token refresh")
                raise ValueError("User not found in database")
                
            refresh_token = db_user.get_google_refresh_token()
            if not refresh_token:
                logger.error(f"User {user_id} ({user_email}) has no refresh token available")
                logger.error("This usually means the user needs to re-authenticate with Google OAuth")
                raise ValueError(f"No refresh token available for user {user_email}. Please sign out and sign in again to re-authenticate with Google.")
            
            creds = Credentials(
                token=None,
                refresh_token=refresh_token,
                client_id=settings.google_client_id,
                client_secret=settings.google_client_secret,
                token_uri="https://oauth2.googleapis.com/token"
            )
            
            creds.refresh(Request())
            
            expires_in = int(creds.expiry.timestamp() - time.time()) if creds.expiry else 3600
            
            # Use raw SQL to avoid session conflicts
            from datetime import datetime, timedelta
            expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
            
            # Update using raw SQL to avoid ORM session issues
            from sqlalchemy import text
            db.execute(
                text("""
                UPDATE users 
                SET google_access_token = :access_token,
                    google_refresh_token = COALESCE(:refresh_token, google_refresh_token),
                    token_expires_at = :expires_at,
                    updated_at = :updated_at
                WHERE id = :user_id
                """),
                {
                    "access_token": User._encrypt_token(creds.token) if creds.token else None,
                    "refresh_token": User._encrypt_token(creds.refresh_token) if creds.refresh_token else None,
                    "expires_at": expires_at,
                    "updated_at": datetime.utcnow(),
                    "user_id": user_id
                }
            )
            
            db.commit()
            logger.info(f"Token refreshed for user {user_id}")
            return creds.token
        finally:
            db.close()
        
    except Exception as e:
        logger.error(f"Token refresh failed: {str(e)}")
        raise ValueError("Token refresh failed. Please re-authenticate.")
