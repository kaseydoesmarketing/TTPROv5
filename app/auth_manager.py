"""
Enhanced Firebase Authentication Manager
Provides robust authentication with automatic token refresh and recovery
"""

import logging
import time
import asyncio
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from functools import wraps
from contextlib import asynccontextmanager

import firebase_admin
from firebase_admin import credentials, auth
import jwt
import requests
from jwt import PyJWKClient

from .config import settings
from .firebase_auth import initialize_firebase

logger = logging.getLogger(__name__)

class AuthenticationError(Exception):
    """Base exception for authentication errors"""
    pass

class TokenExpiredError(AuthenticationError):
    """Token has expired and needs refresh"""
    pass

class TokenInvalidError(AuthenticationError):
    """Token is invalid or malformed"""
    pass

class AuthServiceUnavailableError(AuthenticationError):
    """Authentication service is temporarily unavailable"""
    pass

class FirebaseAuthManager:
    """Enhanced Firebase authentication manager with resilience features"""
    
    def __init__(self):
        self.firebase_initialized = False
        self.initialization_attempts = 0
        self.max_init_attempts = 3
        self.jwks_client = None
        self.last_jwks_refresh = 0
        self.jwks_cache_duration = 3600  # 1 hour
        
    def safe_initialize(self) -> bool:
        """Safely initialize Firebase with retry logic"""
        if self.firebase_initialized:
            return True
            
        for attempt in range(self.max_init_attempts):
            try:
                initialize_firebase()
                self.firebase_initialized = True
                logger.info("✅ Firebase authentication manager initialized")
                return True
                
            except Exception as e:
                self.initialization_attempts += 1
                logger.warning(f"⚠️ Firebase init attempt {attempt + 1} failed: {e}")
                
                if attempt < self.max_init_attempts - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logger.error("❌ Firebase initialization failed after all attempts")
                    
        return False
    
    def get_jwks_client(self) -> PyJWKClient:
        """Get JWKS client with caching and refresh logic"""
        current_time = time.time()
        
        if (not self.jwks_client or 
            current_time - self.last_jwks_refresh > self.jwks_cache_duration):
            
            try:
                self.jwks_client = PyJWKClient(
                    "https://www.googleapis.com/oauth2/v3/certs",
                    cache_keys=True,
                    max_cached_keys=10
                )
                self.last_jwks_refresh = current_time
                logger.debug("🔄 JWKS client refreshed")
                
            except Exception as e:
                logger.warning(f"⚠️ JWKS client refresh failed: {e}")
                if not self.jwks_client:
                    raise AuthServiceUnavailableError("Cannot initialize JWKS client")
        
        return self.jwks_client
    
    def verify_id_token_comprehensive(self, id_token: str) -> Dict[str, Any]:
        """Verify ID token with multiple fallback methods"""
        if not id_token or not id_token.strip():
            raise TokenInvalidError("ID token is required and cannot be empty")
        
        # Try Firebase Admin SDK first (most reliable)
        try:
            if self.safe_initialize():
                decoded_token = auth.verify_id_token(id_token, check_revoked=True)
                logger.debug("✅ Token verified via Firebase Admin SDK")
                return self._normalize_token_data(decoded_token)
                
        except auth.ExpiredIdTokenError:
            raise TokenExpiredError("Token has expired")
        except auth.RevokedIdTokenError:
            raise TokenInvalidError("Token has been revoked")
        except auth.InvalidIdTokenError as e:
            logger.warning(f"⚠️ Firebase Admin SDK verification failed: {e}")
        except Exception as e:
            logger.warning(f"⚠️ Firebase Admin SDK unavailable: {e}")
        
        # Fallback to manual JWT verification
        try:
            return self._verify_token_manually(id_token)
        except Exception as e:
            logger.error(f"❌ Manual token verification failed: {e}")
            raise TokenInvalidError(f"Token verification failed: {str(e)}")
    
    def _verify_token_manually(self, id_token: str) -> Dict[str, Any]:
        """Manually verify JWT token using Google's public keys"""
        try:
            jwks_client = self.get_jwks_client()
            signing_key = jwks_client.get_signing_key_from_jwt(id_token)
            
            decoded_token = jwt.decode(
                id_token,
                signing_key.key,
                algorithms=["RS256"],
                audience=settings.google_client_id,
                issuer=["https://accounts.google.com", "accounts.google.com"],
                options={"verify_exp": True, "verify_iat": True},
                leeway=60  # 1 minute leeway for clock skew
            )
            
            logger.debug("✅ Token verified manually via JWKS")
            return self._normalize_token_data(decoded_token)
            
        except jwt.ExpiredSignatureError:
            raise TokenExpiredError("Token has expired")
        except jwt.InvalidAudienceError:
            raise TokenInvalidError("Invalid token audience")
        except jwt.InvalidIssuerError:
            raise TokenInvalidError("Invalid token issuer")
        except jwt.InvalidTokenError as e:
            raise TokenInvalidError(f"Invalid token: {str(e)}")
    
    def _normalize_token_data(self, decoded_token: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize token data from different sources into consistent format"""
        # Handle both Firebase Admin SDK and manual JWT formats
        user_info = {
            "uid": decoded_token.get("uid") or decoded_token.get("sub"),
            "email": decoded_token.get("email"),
            "name": decoded_token.get("name"),
            "picture": decoded_token.get("picture"),
            "email_verified": decoded_token.get("email_verified", False),
            "auth_time": decoded_token.get("auth_time"),
            "iat": decoded_token.get("iat"),
            "exp": decoded_token.get("exp"),
            "provider_data": decoded_token.get("firebase", {}).get("identities", {}),
            "custom_claims": decoded_token.get("custom_claims", {})
        }
        
        # Validate required fields
        if not user_info["uid"]:
            raise TokenInvalidError("Token missing user ID")
        
        return user_info
    
    def create_custom_token_safe(self, uid: str, additional_claims: Optional[Dict[str, Any]] = None) -> str:
        """Create custom token with error handling and fallbacks"""
        if not uid or not uid.strip():
            raise ValueError("UID is required and cannot be empty")
        
        if not self.safe_initialize():
            raise AuthServiceUnavailableError("Firebase authentication unavailable")
        
        try:
            custom_token = auth.create_custom_token(uid, additional_claims or {})
            
            # Handle both bytes and string returns
            if isinstance(custom_token, bytes):
                return custom_token.decode('utf-8')
            return custom_token
            
        except Exception as e:
            logger.error(f"❌ Custom token creation failed for {uid}: {e}")
            raise AuthServiceUnavailableError(f"Failed to create custom token: {str(e)}")
    
    def refresh_google_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh Google OAuth token with error handling"""
        if not refresh_token:
            raise TokenInvalidError("Refresh token is required")
        
        try:
            token_url = "https://oauth2.googleapis.com/token"
            data = {
                "client_id": settings.google_client_id,
                "client_secret": settings.google_client_secret,
                "refresh_token": refresh_token,
                "grant_type": "refresh_token"
            }
            
            response = requests.post(token_url, data=data, timeout=10)
            
            if response.status_code == 200:
                token_data = response.json()
                logger.info("✅ Google token refreshed successfully")
                return token_data
            elif response.status_code == 400:
                error_data = response.json()
                if error_data.get("error") == "invalid_grant":
                    raise TokenInvalidError("Refresh token is invalid or expired")
                raise TokenInvalidError(f"Token refresh failed: {error_data.get('error_description', 'Unknown error')}")
            else:
                raise AuthServiceUnavailableError(f"Token refresh failed with status {response.status_code}")
                
        except requests.RequestException as e:
            logger.error(f"❌ Token refresh network error: {e}")
            raise AuthServiceUnavailableError("Cannot connect to Google OAuth service")
        except Exception as e:
            logger.error(f"❌ Token refresh failed: {e}")
            raise AuthServiceUnavailableError(f"Token refresh failed: {str(e)}")
    
    def revoke_user_tokens_safe(self, uid: str) -> bool:
        """Safely revoke all user tokens"""
        if not uid:
            return False
        
        try:
            if self.safe_initialize():
                auth.revoke_refresh_tokens(uid)
                logger.info(f"✅ Revoked tokens for user {uid}")
                return True
        except Exception as e:
            logger.error(f"❌ Token revocation failed for {uid}: {e}")
        
        return False
    
    def get_user_safely(self, uid: str) -> Optional[auth.UserRecord]:
        """Safely get user record from Firebase"""
        if not uid or not self.safe_initialize():
            return None
        
        try:
            return auth.get_user(uid)
        except auth.UserNotFoundError:
            logger.warning(f"⚠️ User not found: {uid}")
            return None
        except Exception as e:
            logger.error(f"❌ Failed to get user {uid}: {e}")
            return None
    
    def get_auth_status(self) -> Dict[str, Any]:
        """Get authentication system status"""
        return {
            "firebase_initialized": self.firebase_initialized,
            "initialization_attempts": self.initialization_attempts,
            "jwks_cached": self.jwks_client is not None,
            "last_jwks_refresh": self.last_jwks_refresh,
            "status": "healthy" if self.firebase_initialized else "degraded"
        }

# Global authentication manager
auth_manager = FirebaseAuthManager()

def require_auth(allow_degraded: bool = False):
    """Decorator to require authentication with graceful degradation"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except (TokenExpiredError, TokenInvalidError) as e:
                logger.warning(f"⚠️ Authentication failed: {e}")
                if allow_degraded:
                    # Continue with limited functionality
                    kwargs['auth_degraded'] = True
                    return await func(*args, **kwargs)
                raise
            except AuthServiceUnavailableError as e:
                logger.error(f"❌ Auth service unavailable: {e}")
                if allow_degraded:
                    kwargs['auth_unavailable'] = True
                    return await func(*args, **kwargs)
                raise
        return wrapper
    return decorator

def retry_on_auth_failure(max_retries: int = 2):
    """Decorator to retry operations on authentication failures"""
    def decorator(func):
        if asyncio.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                last_exception = None
                
                for attempt in range(max_retries + 1):
                    try:
                        return await func(*args, **kwargs)
                    except (AuthServiceUnavailableError, TokenExpiredError) as e:
                        last_exception = e
                        if attempt < max_retries:
                            logger.warning(f"⚠️ Auth retry {attempt + 1}/{max_retries}: {e}")
                            await asyncio.sleep(1.5 ** attempt)  # Exponential backoff
                        else:
                            logger.error(f"❌ Auth operation failed after {max_retries} retries")
                    except TokenInvalidError:
                        # Don't retry on invalid tokens
                        raise
                
                raise last_exception
            return async_wrapper
        else:
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                last_exception = None
                
                for attempt in range(max_retries + 1):
                    try:
                        return func(*args, **kwargs)
                    except (AuthServiceUnavailableError, TokenExpiredError) as e:
                        last_exception = e
                        if attempt < max_retries:
                            logger.warning(f"⚠️ Auth retry {attempt + 1}/{max_retries}: {e}")
                            time.sleep(1.5 ** attempt)  # Exponential backoff
                        else:
                            logger.error(f"❌ Auth operation failed after {max_retries} retries")
                    except TokenInvalidError:
                        # Don't retry on invalid tokens
                        raise
                
                raise last_exception
            return sync_wrapper
    return decorator