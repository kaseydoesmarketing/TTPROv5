"""
TTPROv5 Firebase Admin SDK Initialization
Secure SECRET_FILE only configuration with comprehensive logging
"""
import os
import json
import logging
from typing import Optional, Dict, Any
import firebase_admin
from firebase_admin import credentials, auth
from .settings import settings

logger = logging.getLogger(__name__)

# Global Firebase app instance
_firebase_app: Optional[firebase_admin.App] = None

def firebase_debug_payload() -> Dict[str, Any]:
    """Generate Firebase debug information payload"""
    creds_path = settings.GOOGLE_APPLICATION_CREDENTIALS
    
    payload = {
        "configuration_method": "SECRET_FILE",
        "google_application_credentials": os.path.basename(creds_path) if creds_path else None,
        "file_exists": os.path.exists(creds_path) if creds_path else False,
        "firebase_initialized": _firebase_app is not None,
        "allow_env_fallback": settings.ALLOW_ENV_FALLBACK,
        "firebase_debug": settings.FIREBASE_DEBUG
    }
    
    # Add file validation details if debug mode
    if settings.is_debug_mode and creds_path and os.path.exists(creds_path):
        try:
            with open(creds_path, 'r') as f:
                cred_data = json.load(f)
                payload.update({
                    "project_id": cred_data.get("project_id", "missing"),
                    "client_email": cred_data.get("client_email", "missing"),
                    "has_private_key": bool(cred_data.get("private_key")),
                    "credential_type": cred_data.get("type", "unknown")
                })
        except Exception as e:
            payload["file_read_error"] = str(e)
    
    return payload

def initialize_firebase() -> Optional[firebase_admin.App]:
    """
    Initialize Firebase Admin SDK using SECRET_FILE method only
    Returns Firebase app instance or None if initialization fails
    """
    global _firebase_app
    
    if _firebase_app:
        logger.info("✅ Firebase already initialized")
        return _firebase_app
    
    creds_path = settings.GOOGLE_APPLICATION_CREDENTIALS
    logger.info(f"🔥 Initializing Firebase Admin SDK...")
    logger.info(f"📁 Credentials path: {creds_path}")
    logger.info(f"🔒 Allow env fallback: {settings.ALLOW_ENV_FALLBACK}")
    logger.info(f"🐛 Debug mode: {settings.is_debug_mode}")
    
    # Validate secret file exists
    if not os.path.exists(creds_path):
        logger.error(f"❌ Firebase secret file not found: {creds_path}")
        logger.error("🚨 CRITICAL: Firebase initialization failed - no secret file")
        return None
    
    try:
        # Read and validate secret file content
        with open(creds_path, 'r') as f:
            cred_data = json.load(f)
            
        # Validate required fields
        required_fields = ["project_id", "private_key", "client_email", "type"]
        missing_fields = [field for field in required_fields if not cred_data.get(field)]
        
        if missing_fields:
            logger.error(f"❌ Firebase secret file missing required fields: {missing_fields}")
            return None
        
        # Initialize Firebase with service account credentials
        cred = credentials.Certificate(creds_path)
        _firebase_app = firebase_admin.initialize_app(cred)
        
        # Verify initialization with a test call
        try:
            # Test by attempting to decode a dummy token (will fail but proves SDK works)
            auth.verify_id_token("dummy_token", check_revoked=False)
        except firebase_admin.auth.InvalidIdTokenError:
            # Expected error - means SDK is working
            pass
        except Exception as e:
            logger.warning(f"⚠️ Firebase test call warning: {e}")
        
        logger.info("✅ Firebase Admin SDK initialized successfully")
        logger.info(f"📊 Project ID: {cred_data['project_id']}")
        logger.info(f"📧 Service Account: {cred_data['client_email'][:20]}...")
        
        return _firebase_app
        
    except json.JSONDecodeError as e:
        logger.error(f"❌ Firebase secret file contains invalid JSON: {e}")
        return None
    except ValueError as e:
        logger.error(f"❌ Firebase credential validation failed: {e}")
        return None
    except Exception as e:
        logger.error(f"❌ Firebase initialization failed: {e}")
        return None

def get_firebase_app() -> Optional[firebase_admin.App]:
    """Get the initialized Firebase app instance"""
    return _firebase_app

def verify_firebase_token(id_token: str) -> Optional[Dict[str, Any]]:
    """
    Verify Firebase ID token and return decoded claims
    Returns None if verification fails
    """
    if not _firebase_app:
        logger.error("❌ Firebase not initialized - cannot verify token")
        return None
    
    try:
        # Verify the ID token
        decoded_token = auth.verify_id_token(id_token, check_revoked=True)
        logger.info(f"✅ Token verified for user: {decoded_token.get('uid', 'unknown')}")
        return decoded_token
    except auth.InvalidIdTokenError as e:
        logger.warning(f"⚠️ Invalid Firebase token: {e}")
        return None
    except auth.ExpiredIdTokenError:
        logger.warning("⚠️ Firebase token expired")
        return None
    except auth.RevokedIdTokenError:
        logger.warning("⚠️ Firebase token revoked")
        return None
    except Exception as e:
        logger.error(f"❌ Firebase token verification failed: {e}")
        return None

def get_user_info(uid: str) -> Optional[Dict[str, Any]]:
    """Get user information from Firebase Auth"""
    if not _firebase_app:
        logger.error("❌ Firebase not initialized - cannot get user info")
        return None
    
    try:
        user_record = auth.get_user(uid)
        return {
            "uid": user_record.uid,
            "email": user_record.email,
            "email_verified": user_record.email_verified,
            "display_name": user_record.display_name,
            "photo_url": user_record.photo_url,
            "disabled": user_record.disabled
        }
    except auth.UserNotFoundError:
        logger.warning(f"⚠️ User not found: {uid}")
        return None
    except Exception as e:
        logger.error(f"❌ Failed to get user info: {e}")
        return None

# Initialize Firebase when module is imported
logger.info("🚀 Loading Firebase module...")
_firebase_app = initialize_firebase()