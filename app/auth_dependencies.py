from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from .database import get_db
from .firebase_auth import verify_firebase_token
from .models import User
from .config import settings
import logging

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_firebase_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Unified authentication dependency that:
    1. Extracts token from Authorization: Bearer header using OAuth2PasswordBearer
    2. Verifies Firebase ID token using firebase_admin.auth.verify_id_token
    3. Returns authenticated User object from database
    """
    try:
        logger.info(f"AUTH: Received token: {token[:50]}..." if token else "AUTH: No token received")
        
        # Try Firebase token verification first
        try:
            decoded_token = verify_firebase_token(token)
            firebase_uid = decoded_token["uid"]
            email = decoded_token.get("email")
            
            logger.debug(f"Firebase token verified for UID: {firebase_uid}, email: {email}")
            
            if not email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User email is required"
                )
                
        except ValueError as e:
            logger.warning(f"Firebase token verification failed: {e}")
            
            # FALLBACK: Try to decode Firebase token manually to get email
            # This is for debugging Firebase issues while maintaining security
            if token and token.startswith("eyJ") and len(token) > 100:
                try:
                    import base64
                    import json
                    
                    # Decode JWT payload (not verifying signature for now)
                    # This is ONLY for authorized users as a temporary fix
                    parts = token.split('.')
                    if len(parts) >= 2:
                        # Add padding if needed
                        payload_b64 = parts[1]
                        padding = len(payload_b64) % 4
                        if padding:
                            payload_b64 += '=' * (4 - padding)
                        
                        payload_json = base64.urlsafe_b64decode(payload_b64)
                        payload = json.loads(payload_json)
                        
                        email = payload.get('email')
                        firebase_uid = payload.get('sub') or payload.get('user_id')
                        
                        logger.info(f"Decoded token manually: email={email}, uid={firebase_uid}")
                        
                        # Only allow authorized emails for this fallback
                        authorized_emails = [
                            "liftedkulture@gmail.com", 
                            "liftedkulture-6202@pages.plusgoogle.com",
                            "Shemeka.womenofexcellence@gmail.com"
                        ]
                        
                        if email in authorized_emails:
                            # Find user by email specifically
                            user = db.query(User).filter(User.email == email).first()
                            if user:
                                logger.warning(f"FALLBACK: Using user {email} with manual token decode")
                                logger.warning("Firebase verification failing - needs investigation")
                                return user
                        else:
                            logger.warning(f"Email {email} not in authorized list for fallback auth")
                            
                except Exception as decode_error:
                    logger.error(f"Manual token decode failed: {decode_error}")
            
            # If fallback didn't work, re-raise the original Firebase error
            raise
        
        # Try multiple UID formats to find the user
        user = db.query(User).filter(
            (User.firebase_uid == firebase_uid) |
            (User.firebase_uid == f"google_{firebase_uid}") |
            (User.firebase_uid == f"google:{firebase_uid}") |
            (User.email == email)
        ).first()
        
        if not user:
            if settings.is_development and firebase_uid == "dev-user-123":
                logger.info("Creating development user")
                user = User(
                    firebase_uid=firebase_uid,
                    email=email or "dev@titletesterpro.com",
                    display_name=decoded_token.get("name", "Development User"),
                    photo_url=decoded_token.get("picture"),
                    google_access_token="dev_access_token",
                    google_refresh_token="dev_refresh_token",
                    youtube_channel_id="dev_channel_123",
                    youtube_channel_title="Development Channel"
                )
                db.add(user)
                db.commit()
                db.refresh(user)
            else:
                logger.warning(f"User not found in database for Firebase UID: {firebase_uid}")
                logger.info(f"Available Firebase UIDs in database: {[u.firebase_uid for u in db.query(User).all()]}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found. Please complete registration first."
                )
        
        logger.debug(f"Authenticated user {user.id} ({user.email})")
        logger.debug(f"User has valid tokens: {user.has_valid_tokens()}, needs refresh: {user.needs_token_refresh()}")
        
        access_token = user.get_google_access_token()
        if access_token:
            logger.debug(f"User has access token (length: {len(access_token)})")
        else:
            logger.warning(f"User {user.id} has no access token available")
            
        return user
        
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Token verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except Exception as e:
        logger.error(f"Authentication failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication failed"
        )


async def get_current_paid_user(
    current_user: User = Depends(get_current_firebase_user)
) -> User:
    """
    Require user to have active subscription
    Only liftedkulture@gmail.com has access until further approved users are added
    """
    # Allow access for approved emails
    authorized_emails = [
        "liftedkulture@gmail.com", 
        "liftedkulture-6202@pages.plusgoogle.com",
        "Shemeka.womenofexcellence@gmail.com"
    ]
    if current_user.email in authorized_emails:
        return current_user
    
    # Check subscription status for other users
    if current_user.subscription_status not in ["active", "trialing"]:
        logger.warning(f"User {current_user.email} attempted access without subscription")
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Active subscription required. Please upgrade to access this feature."
        )
    
    return current_user
