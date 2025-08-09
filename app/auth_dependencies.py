from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from .database import get_db
from .firebase_auth import verify_firebase_token
from .auth_manager import (
    auth_manager, 
    TokenExpiredError, 
    TokenInvalidError, 
    AuthServiceUnavailableError,
    retry_on_auth_failure
)
from .models import User
from .config import settings
import logging
import hashlib
from datetime import datetime

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@retry_on_auth_failure(max_retries=2)
async def get_current_firebase_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Enhanced authentication dependency with comprehensive error handling:
    1. Uses robust auth manager with multiple verification methods
    2. Handles token expiration and automatic refresh
    3. Provides graceful fallbacks for service unavailability
    4. Returns authenticated User object from database
    """
    try:
        logger.debug(f"AUTH: Processing token for user authentication")
        
        # Use enhanced auth manager for token verification
        try:
            decoded_token = auth_manager.verify_id_token_comprehensive(token)
            firebase_uid = decoded_token["uid"]
            email = decoded_token.get("email")
            
            logger.debug(f"✅ Token verified for UID: {firebase_uid}, email: {email}")
            
        except TokenExpiredError:
            logger.warning("⚠️ Token expired - client should refresh")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired. Please refresh your authentication.",
                headers={"WWW-Authenticate": "Bearer", "X-Auth-Error": "token_expired"}
            )
            
        except TokenInvalidError as e:
            logger.warning(f"⚠️ Invalid token: {e}")
            
            # Fallback for debugging - only for authorized emails
            if _try_emergency_fallback(token, db) is not None:
                return _try_emergency_fallback(token, db)
            
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token. Please sign in again.",
                headers={"WWW-Authenticate": "Bearer", "X-Auth-Error": "token_invalid"}
            )
            
        except AuthServiceUnavailableError as e:
            logger.error(f"❌ Auth service unavailable: {e}")
            
            # Try emergency fallback for critical operations
            fallback_user = _try_emergency_fallback(token, db)
            if fallback_user:
                logger.warning("🚨 Using emergency authentication fallback")
                return fallback_user
            
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Authentication service temporarily unavailable. Please try again.",
                headers={"Retry-After": "30"}
            )
        
        # Find user in database with multiple fallback strategies
        user = _find_user_by_uid_and_email(db, firebase_uid, email)
        
        if not user:
            # Handle development user creation
            if settings.is_development and firebase_uid == "dev-user-123":
                user = _create_development_user(db, decoded_token)
            else:
                logger.warning(f"⚠️ User not found for UID: {firebase_uid}, email: {email}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found. Please complete registration first.",
                    headers={"X-Auth-Error": "user_not_found"}
                )
        
        # Check and refresh tokens if needed
        await _ensure_user_tokens_valid(user, db)
        
        logger.debug(f"✅ User {user.id} ({user.email}) authenticated successfully")
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Unexpected authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication system error. Please try again.",
            headers={"X-Auth-Error": "system_error"}
        )

def _find_user_by_uid_and_email(db: Session, firebase_uid: str, email: str) -> Optional[User]:
    """Find user by Firebase UID or email with multiple format fallbacks"""
    # Try multiple UID formats for backwards compatibility
    uid_formats = [
        firebase_uid,
        f"google_{firebase_uid}",
        f"google:{firebase_uid}"
    ]
    
    for uid_format in uid_formats:
        user = db.query(User).filter(User.firebase_uid == uid_format).first()
        if user:
            # Update UID to canonical format if needed
            if user.firebase_uid != firebase_uid:
                user.firebase_uid = firebase_uid
                db.commit()
            return user
    
    # Fallback: find by email
    if email:
        return db.query(User).filter(User.email == email).first()
    
    return None

def _create_development_user(db: Session, decoded_token: Dict[str, Any]) -> User:
    """Create development user for testing"""
    logger.info("🔧 Creating development user")
    user = User(
        firebase_uid=decoded_token["uid"],
        email=decoded_token.get("email", "dev@titletesterpro.com"),
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
    return user

async def _ensure_user_tokens_valid(user: User, db: Session):
    """Ensure user's Google tokens are valid and refresh if needed"""
    try:
        if user.needs_token_refresh():
            refresh_token = user.get_google_refresh_token()
            if refresh_token:
                logger.info(f"🔄 Refreshing tokens for user {user.id}")
                try:
                    new_tokens = auth_manager.refresh_google_token(refresh_token)
                    user.set_google_tokens(
                        access_token=new_tokens.get("access_token"),
                        refresh_token=new_tokens.get("refresh_token", refresh_token)
                    )
                    db.commit()
                    logger.info(f"✅ Tokens refreshed for user {user.id}")
                except Exception as e:
                    logger.warning(f"⚠️ Token refresh failed for user {user.id}: {e}")
    except Exception as e:
        logger.warning(f"⚠️ Token validation check failed for user {user.id}: {e}")

def _try_emergency_fallback(token: str, db: Session) -> Optional[User]:
    """Emergency fallback authentication for critical situations"""
    try:
        if not token or not token.startswith("eyJ"):
            return None
        
        import base64
        import json
        
        # Decode JWT payload without signature verification
        parts = token.split('.')
        if len(parts) < 2:
            return None
        
        payload_b64 = parts[1]
        padding = len(payload_b64) % 4
        if padding:
            payload_b64 += '=' * (4 - padding)
        
        payload_json = base64.urlsafe_b64decode(payload_b64)
        payload = json.loads(payload_json)
        
        email = payload.get('email')
        
        # Only allow for pre-authorized emergency access
        emergency_emails = [
            "liftedkulture@gmail.com", 
            "liftedkulture-6202@pages.plusgoogle.com",
            "Shemeka.womenofexcellence@gmail.com"
        ]
        
        if email in emergency_emails:
            user = db.query(User).filter(User.email == email).first()
            if user:
                logger.warning(f"🚨 EMERGENCY FALLBACK: Authenticated {email}")
                return user
        
    except Exception as e:
        logger.debug(f"Emergency fallback failed: {e}")
    
    return None


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


async def get_current_user_session(
    request: Request,
    db: Session = Depends(get_db)
) -> User:
    """
    Get current user from session cookie instead of Firebase token.
    This enables persistent login without requiring the Firebase token on every request.
    """
    try:
        # Get session token from cookie
        session_token = request.cookies.get("session_token")
        
        if not session_token:
            logger.debug("No session token found in cookies")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No active session. Please sign in.",
                headers={"WWW-Authenticate": "Session"}
            )
        
        # Hash the session token for database lookup
        session_hash = hashlib.sha256(session_token.encode()).hexdigest()
        
        # Find user with this session token
        user = db.query(User).filter(
            User.session_token == session_hash,
            User.session_expires > datetime.utcnow(),
            User.is_active == True
        ).first()
        
        if not user:
            logger.debug("Invalid or expired session token")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Session expired or invalid. Please sign in again.",
                headers={"WWW-Authenticate": "Session"}
            )
        
        logger.debug(f"✅ Session authenticated for user {user.id} ({user.email})")
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Session authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication system error. Please try again."
        )
