import firebase_admin
from firebase_admin import credentials, auth
from .config import settings
import logging
from typing import Dict, Any, Optional
import json
import os

logger = logging.getLogger(__name__)

_firebase_initialized = False


def initialize_firebase():
    """Initialize Firebase Admin SDK with secure service account file or fallback to environment variables"""
    global _firebase_initialized
    
    if _firebase_initialized:
        return
        
    if not firebase_admin._apps:
        try:
            # Method 1: Use GOOGLE_APPLICATION_CREDENTIALS (Render Secret File) - PREFERRED
            if os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
                service_account_path = os.environ["GOOGLE_APPLICATION_CREDENTIALS"]
                logger.info(f"Using Firebase service account file: {service_account_path}")
                
                # Verify file exists and is readable
                if not os.path.exists(service_account_path):
                    raise FileNotFoundError(f"Firebase service account file not found: {service_account_path}")
                
                try:
                    cred = credentials.Certificate(service_account_path)
                    firebase_admin.initialize_app(cred)
                    _firebase_initialized = True
                    logger.info("✅ Firebase Admin SDK initialized successfully using service account file")
                    return
                except Exception as e:
                    logger.error(f"❌ Failed to initialize Firebase with service account file: {e}")
                    raise
            
            # Method 2: Fallback to environment variables (LESS SECURE)
            logger.warning("⚠️ GOOGLE_APPLICATION_CREDENTIALS not set, falling back to environment variables")
            
            if settings.is_development:
                # Development mode: more lenient error handling
                required_fields = [
                    settings.firebase_project_id,
                    settings.firebase_private_key_id,
                    settings.firebase_private_key,
                    settings.firebase_client_email,
                    settings.firebase_client_id
                ]
                
                if (settings.firebase_private_key == "-----BEGIN PRIVATE KEY-----\ntest_private_key_content\n-----END PRIVATE KEY-----\n" or
                    "test_" in settings.firebase_project_id):
                    logger.warning("Development mode: Skipping Firebase initialization due to test credentials")
                    _firebase_initialized = True
                    return
                
                if not all(required_fields):
                    logger.warning("Development mode: Skipping Firebase initialization due to missing credentials")
                    _firebase_initialized = True
                    return
            else:
                # Production mode: strict validation
                required_fields = [
                    settings.firebase_project_id,
                    settings.firebase_private_key_id,
                    settings.firebase_private_key,
                    settings.firebase_client_email,
                    settings.firebase_client_id
                ]
                
                if not all(required_fields):
                    missing = []
                    if not settings.firebase_project_id:
                        missing.append("FIREBASE_PROJECT_ID")
                    if not settings.firebase_private_key_id:
                        missing.append("FIREBASE_PRIVATE_KEY_ID")
                    if not settings.firebase_private_key:
                        missing.append("FIREBASE_PRIVATE_KEY")
                    if not settings.firebase_client_email:
                        missing.append("FIREBASE_CLIENT_EMAIL")
                    if not settings.firebase_client_id:
                        missing.append("FIREBASE_CLIENT_ID")
                    
                    raise ValueError(f"Missing required Firebase Admin SDK configuration: {', '.join(missing)}")
            
            # Create credential dictionary from environment variables
            cred_dict = {
                "type": "service_account",
                "project_id": settings.firebase_project_id,
                "private_key_id": settings.firebase_private_key_id,
                "private_key": settings.firebase_private_key.replace('\\n', '\n'),
                "client_email": settings.firebase_client_email,
                "client_id": settings.firebase_client_id,
                "auth_uri": settings.firebase_auth_uri,
                "token_uri": settings.firebase_token_uri,
                "auth_provider_x509_cert_url": settings.firebase_auth_provider_x509_cert_url,
                "client_x509_cert_url": settings.firebase_client_x509_cert_url or f"https://www.googleapis.com/robot/v1/metadata/x509/{settings.firebase_client_email}"
            }
            
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred)
            _firebase_initialized = True
            logger.info("✅ Firebase Admin SDK initialized successfully using environment variables")
                
        except Exception as e:
            if settings.is_development:
                logger.warning(f"Development mode: Firebase initialization failed, continuing without Firebase: {e}")
                _firebase_initialized = True
                return
            else:
                logger.error(f"Firebase initialization failed: {e}")
                raise RuntimeError(f"Failed to initialize Firebase Admin SDK: {str(e)}")


def verify_firebase_token(id_token: str) -> Dict[str, Any]:
    """
    Verify Firebase ID token and return user info - with development bypass
    
    Args:
        id_token: Firebase ID token from client
        
    Returns:
        Dict containing user information
        
    Raises:
        ValueError: If token is invalid or missing required fields
        RuntimeError: If Firebase initialization fails
    """
    if not id_token or not id_token.strip():
        raise ValueError("ID token is required and cannot be empty")
    
    # Development mode: bypass Firebase verification for dev token
    if settings.is_development and id_token == "dev-id-token":
        logger.info("Development mode: Using mock authentication token")
        return {
            "uid": "dev-user-123",
            "email": "dev@titletesterpro.com",
            "name": "Development User",
            "picture": "https://via.placeholder.com/100",
            "email_verified": True,
            "provider_data": {},
            "auth_time": 1640995200,  # Mock timestamp
            "iat": 1640995200,
            "exp": 9999999999  # Far future expiry
        }
    
    try:
        initialize_firebase()
        decoded_token = auth.verify_id_token(id_token, check_revoked=True)
        
        # Debug: Log token structure to understand custom token format
        logger.info(f"DEBUG: Decoded token keys: {list(decoded_token.keys())}")
        logger.info(f"DEBUG: Decoded token: {decoded_token}")
        
        required_fields = ["uid"]  # Remove email requirement temporarily for debugging
        for field in required_fields:
            if field not in decoded_token:
                raise ValueError(f"Token missing required field: {field}")
        
        if not decoded_token.get("email_verified", False):
            logger.warning(f"User {decoded_token['uid']} has unverified email")
        
        # For custom tokens, email might be in custom claims or main token
        email = decoded_token.get("email")
        if not email and "custom_claims" in decoded_token:
            email = decoded_token.get("custom_claims", {}).get("email")
        if not email:
            # Try direct access to additional claims
            email = decoded_token.get("email")
        
        user_info = {
            "uid": decoded_token["uid"],
            "email": email or decoded_token.get("email"),
            "name": decoded_token.get("name"),
            "picture": decoded_token.get("picture"),
            "email_verified": decoded_token.get("email_verified", False),
            "provider_data": decoded_token.get("firebase", {}).get("identities", {}),
            "auth_time": decoded_token.get("auth_time"),
            "iat": decoded_token.get("iat"),
            "exp": decoded_token.get("exp")
        }
        
        logger.info(f"Successfully verified token for user {user_info['uid']}")
        return user_info
        
    except auth.InvalidIdTokenError as e:
        logger.error(f"Invalid ID token: {e}")
        raise ValueError(f"Invalid or expired token: {str(e)}")
    except auth.ExpiredIdTokenError as e:
        logger.error(f"Expired ID token: {e}")
        raise ValueError("Token has expired, please sign in again")
    except auth.RevokedIdTokenError as e:
        logger.error(f"Revoked ID token: {e}")
        raise ValueError("Token has been revoked, please sign in again")
    except Exception as e:
        logger.error(f"Token verification failed: {e}")
        raise ValueError(f"Token verification failed: {str(e)}")


async def get_user_by_uid(uid: str) -> Optional[auth.UserRecord]:
    """
    Get user info from Firebase by UID
    
    Args:
        uid: Firebase user UID
        
    Returns:
        Firebase UserRecord or None if not found
        
    Raises:
        ValueError: If UID is invalid
        RuntimeError: If Firebase initialization fails
    """
    if not uid or not uid.strip():
        raise ValueError("UID is required and cannot be empty")
        
    try:
        initialize_firebase()
        user_record = auth.get_user(uid)
        logger.info(f"Successfully retrieved user record for UID {uid}")
        return user_record
    except auth.UserNotFoundError:
        logger.warning(f"User not found for UID {uid}")
        return None
    except Exception as e:
        logger.error(f"Failed to get user by UID {uid}: {e}")
        raise RuntimeError(f"Failed to retrieve user: {str(e)}")


def create_custom_token(uid: str, additional_claims: Optional[Dict[str, Any]] = None) -> str:
    """
    Create a custom token for a user (useful for server-side authentication)
    
    Args:
        uid: Firebase user UID
        additional_claims: Optional additional claims to include in token
        
    Returns:
        Custom token string
        
    Raises:
        ValueError: If UID is invalid
        RuntimeError: If Firebase initialization fails
    """
    if not uid or not uid.strip():
        raise ValueError("UID is required and cannot be empty")
        
    try:
        initialize_firebase()
        custom_token = auth.create_custom_token(uid, additional_claims)
        logger.info(f"Created custom token for user {uid}")
        
        # Handle both bytes and string returns from Firebase Admin SDK
        if isinstance(custom_token, bytes):
            return custom_token.decode('utf-8')
        else:
            return custom_token
    except Exception as e:
        logger.error(f"Failed to create custom token for UID {uid}: {e}")
        raise RuntimeError(f"Failed to create custom token: {str(e)}")


def revoke_refresh_tokens(uid: str) -> None:
    """
    Revoke all refresh tokens for a user (useful for logout/security)
    
    Args:
        uid: Firebase user UID
        
    Raises:
        ValueError: If UID is invalid
        RuntimeError: If Firebase initialization fails
    """
    if not uid or not uid.strip():
        raise ValueError("UID is required and cannot be empty")
        
    try:
        initialize_firebase()
        auth.revoke_refresh_tokens(uid)
        logger.info(f"Revoked refresh tokens for user {uid}")
    except Exception as e:
        logger.error(f"Failed to revoke refresh tokens for UID {uid}: {e}")
        raise RuntimeError(f"Failed to revoke refresh tokens: {str(e)}")
