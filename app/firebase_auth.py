import firebase_admin
from firebase_admin import credentials, auth
from .config import settings
import logging
from typing import Dict, Any, Optional
import json
import os

logger = logging.getLogger(__name__)

_firebase_initialized = False


def _peek_jwt_claims(jwt_str: str) -> Optional[Dict[str, Any]]:
    """Safely decode JWT claims for debugging (only when FIREBASE_DEBUG=1)"""
    if os.getenv("FIREBASE_DEBUG", "0") != "1":
        return None
        
    try:
        import base64
        import json
        
        if not jwt_str or "." not in jwt_str:
            logger.warning("[JWT PEEK] Invalid token format")
            return None
            
        parts = jwt_str.split(".")
        if len(parts) != 3:
            logger.warning(f"[JWT PEEK] Invalid JWT parts count: {len(parts)}")
            return None
            
        # Decode payload
        payload_b64 = parts[1]
        # Add padding for base64 decoding
        payload_b64 += "=" * (-len(payload_b64) % 4)
        
        payload = json.loads(base64.urlsafe_b64decode(payload_b64).decode())
        
        # Extract safe claims for debugging
        safe_payload = {
            k: v for k, v in payload.items() 
            if k in ("iss", "aud", "sub", "user_id", "firebase", "exp", "iat", "auth_time", "email", "name")
        }
        
        logger.info(f"[JWT PEEK] payload={safe_payload}")
        
        # Critical project checks
        expected_project = "titletesterpro"
        aud = safe_payload.get("aud")
        iss = safe_payload.get("iss")
        
        if aud != expected_project:
            logger.error(f"[JWT PEEK] ❌ AUDIENCE MISMATCH: got '{aud}', expected '{expected_project}'")
        else:
            logger.info(f"[JWT PEEK] ✅ Audience matches: {aud}")
            
        expected_iss = f"https://securetoken.google.com/{expected_project}"
        if iss != expected_iss:
            logger.error(f"[JWT PEEK] ❌ ISSUER MISMATCH: got '{iss}', expected '{expected_iss}'")
        else:
            logger.info(f"[JWT PEEK] ✅ Issuer matches: {iss}")
            
        return safe_payload
    except Exception as e:
        logger.error(f"[JWT PEEK] Failed to inspect token: {e}")
        return None


def _get_secret_file_path() -> str:
    """
    Return the only allowed service account path.
    Accept GOOGLE_APPLICATION_CREDENTIALS only if it exactly equals this path.
    """
    secret_path = "/etc/secrets/firebase-service-account.json"
    gac = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if gac and gac != secret_path:
        pass
    return secret_path


def initialize_firebase():
    """Initialize Firebase Admin SDK from file-only secret"""
    global _firebase_initialized

    if _firebase_initialized:
        return

    if not firebase_admin._apps:
        try:
            service_account_path = _get_secret_file_path()

            if not os.path.exists(service_account_path) or not os.path.isfile(service_account_path):
                raise FileNotFoundError("Service account file not found at expected path")

            if not os.access(service_account_path, os.R_OK):
                raise PermissionError("Service account file is not readable")

            with open(service_account_path, "r") as f:
                service_data = json.load(f)

            required_fields = ["type", "project_id", "private_key", "client_email"]
            missing = [k for k in required_fields if k not in service_data]
            if missing:
                raise ValueError(f"Service account file missing required fields: {missing}")

            if service_data.get("project_id") != "titletesterpro":
                raise ValueError("Service account project_id mismatch")

            cred = credentials.Certificate(service_account_path)
            firebase_admin.initialize_app(cred, {"projectId": "titletesterpro"})
            _firebase_initialized = True
            logger.info("Firebase Admin initialized from SECRET_FILE")
        except Exception as e:
            logger.error(f"Firebase initialization failed: {e}")
            raise RuntimeError("Failed to initialize Firebase Admin SDK")


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
        # Debug JWT inspection (only when FIREBASE_DEBUG=1)
        _peek_jwt_claims(id_token)
        
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
