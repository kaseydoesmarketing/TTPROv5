from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from .config import settings
from .database import get_db
from .firebase_auth import verify_firebase_token, initialize_firebase
from .models import User
from .ab_test_routes import router as ab_test_router
from .channel_routes import router as channel_router
from .billing_routes import router as billing_router
from .admin_routes import router as admin_router
from .auth_dependencies import get_current_firebase_user
import logging
import asyncio
import requests
from firebase_admin import auth as firebase_auth
import jwt
from jwt import PyJWKClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

processed_auth_codes = set()

app = FastAPI(
    title="TitleTesterPro API",
    description="A SaaS platform for A/B testing YouTube titles - Non-blocking Database",
    version="1.0.2"
)

# CRITICAL: Health check endpoint MUST be defined before ANY middleware
# This ensures Render can always reach it during deployment
@app.get("/")
def root():
    """Root endpoint for Render health checks"""
    return {"status": "healthy", "service": "TitleTesterPro API", "platform": "render"}

@app.get("/healthz")
def healthz():
    """Health check endpoint"""
    return {"status": "ok"}

@app.get("/health")
async def health_check_simple():
    """Simple health check that responds immediately without database dependencies"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "titletesterpro-api"
    }

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)

app.include_router(ab_test_router)
app.include_router(channel_router)
app.include_router(billing_router, prefix="/api")
app.include_router(admin_router)

@app.on_event("startup")
async def startup_event():
    """Non-blocking startup - health endpoints available immediately"""
    logger.info("🚀 TitleTesterPro starting with simplified database connection...")
    logger.info(f"🔧 Environment: {settings.environment}")
    logger.info(f"🔧 Database URL configured: {'Yes' if settings.database_url else 'No'}")
    logger.info(f"🔧 Firebase Project ID: {settings.firebase_project_id[:10]}..." if settings.firebase_project_id else "Not set")
    
    # Initialize startup status first - app can serve health checks immediately
    app.state.startup_status = {
        "status": "starting",
        "database_available": False,
        "firebase_available": False,
        "redis_available": False,
        "errors": [],
        "can_process_requests": True,
        "environment_safe": True  # Allow health checks even with missing env vars
    }
    
    # Firebase initialization in background - don't block startup
    async def init_firebase_async():
        try:
            # Add timeout to prevent hanging
            await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(None, initialize_firebase),
                timeout=5.0  # 5 second timeout
            )
            app.state.startup_status["firebase_available"] = True
            logger.info("✅ Firebase initialized successfully")
        except asyncio.TimeoutError:
            logger.warning("⚠️ Firebase initialization timeout - continuing without Firebase")
            app.state.startup_status["firebase_available"] = False
            app.state.startup_status["errors"].append("Firebase: Initialization timeout")
        except Exception as e:
            logger.warning(f"⚠️ Firebase initialization failed: {e} - continuing without Firebase")
            app.state.startup_status["firebase_available"] = False
            app.state.startup_status["errors"].append(f"Firebase: {str(e)}")
    
    # Start Firebase init in background
    asyncio.create_task(init_firebase_async())
    
    # Initialize database with proper Railway pattern - don't block startup
    logger.info("🔄 Skipping database initialization during startup to prevent blocking")
    app.state.startup_status["database_available"] = False
    app.state.startup_status["errors"].append("Database: Lazy initialization - will connect on first use")
    
    # Update status - app is ready to serve requests
    app.state.startup_status["status"] = "healthy"
    logger.info("✅ App startup completed - health endpoints ready")

@app.get("/api/quota/usage")
async def get_quota_usage(current_user: User = Depends(get_current_firebase_user), db: Session = Depends(get_db)):
    """Get current user's API quota usage"""
    try:
        from .models import QuotaUsage
        from datetime import datetime, timedelta
        
        today = datetime.utcnow().date()
        
        quota_record = db.query(QuotaUsage).filter(
            QuotaUsage.user_id == current_user.id,
            QuotaUsage.date >= today,
            QuotaUsage.date < today + timedelta(days=1)
        ).first()
        
        if not quota_record:
            return {
                "quota_units_used": 0,
                "daily_limit": 10000,
                "percentage_used": 0.0
            }
        
        daily_limit = 10000
        percentage_used = (quota_record.quota_units_used / daily_limit) * 100
        
        return {
            "quota_units_used": quota_record.quota_units_used,
            "daily_limit": daily_limit,
            "percentage_used": min(percentage_used, 100.0)
        }
        
    except Exception as e:
        logger.error(f"Error fetching quota usage: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch quota usage"
        )

security = HTTPBearer()


@app.get("/")
def read_root():
    return {
        "message": "TitleTesterPro API",
        "version": "1.0.2",
        "status": "healthy"
    }


@app.get("/health")
def health_check():
    """Comprehensive health check with environment and service status"""
    try:
        from .env_validator import env_validator
        
        # Get startup status if available
        startup_status = getattr(app.state, 'startup_status', {
            "status": "unknown",
            "database_available": False,
            "redis_available": False,
            "firebase_available": False,
            "environment_safe": False,
            "errors": ["Startup status not available"]
        })
        
        # Get environment health data
        env_health = env_validator.get_health_check_data()
        
        # Determine overall health
        overall_status = "healthy"
        if not startup_status.get("environment_safe", False):
            overall_status = "emergency"
        elif not startup_status.get("firebase_available", False):
            overall_status = "degraded"
        elif startup_status.get("status") in ["emergency", "degraded"]:
            overall_status = startup_status["status"]
            
        return {
            "status": overall_status,
            "timestamp": datetime.utcnow().isoformat(),
            "deployment_version": "1.0.1-railway",
            "deployment_time": "2025-08-04T05:45:00Z",
            "environment": env_health,
            "services": {
                "database": "available" if startup_status.get("database_available", False) else "unavailable",
                "redis": "available" if startup_status.get("redis_available", False) else "unavailable", 
                "firebase": "available" if startup_status.get("firebase_available", False) else "unavailable"
            },
            "startup": {
                "status": startup_status.get("status", "unknown"),
                "environment_safe": startup_status.get("environment_safe", False),
                "errors": startup_status.get("errors", [])
            },
            "can_process_requests": startup_status.get("environment_safe", False) and startup_status.get("firebase_available", False)
        }
    except Exception as e:
        # Even health check should never crash
        logger.error(f"Health check failed: {e}")
        return {
            "status": "emergency",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e),
            "message": "Health check system failure"
        }

@app.get("/health-detailed")
def detailed_health_check():
    """Detailed health check with full environment variable status"""
    try:
        from .env_validator import env_validator
        
        # Get comprehensive status
        startup_status = getattr(app.state, 'startup_status', {})
        env_summary = env_validator.get_status_summary()
        
        # Test each service with detailed info
        service_details = {}
        
        # Database details
        try:
            from .database import SessionLocal
            db = SessionLocal()
            db.execute("SELECT 1")
            db.close()
            service_details["database"] = {
                "status": "healthy",
                "connection": "successful",
                "type": "postgresql" if "postgresql" in str(startup_status.get("database_url", "")) else "sqlite"
            }
        except Exception as e:
            service_details["database"] = {
                "status": "unhealthy",
                "error": str(e),
                "connection": "failed"
            }
        
        # Redis details
        try:
            import redis
            from .config import settings
            r = redis.from_url(settings.redis_url, socket_timeout=2)
            r.ping()
            service_details["redis"] = {
                "status": "healthy",
                "connection": "successful"
            }
        except Exception as e:
            service_details["redis"] = {
                "status": "unhealthy", 
                "error": str(e),
                "connection": "failed"
            }
        
        # Firebase details
        try:
            from .firebase_auth import create_custom_token
            create_custom_token("health_check", {"test": True})
            service_details["firebase"] = {
                "status": "healthy",
                "can_create_tokens": True
            }
        except Exception as e:
            service_details["firebase"] = {
                "status": "unhealthy",
                "error": str(e),
                "can_create_tokens": False
            }
        
        return {
            "status": "detailed_check",
            "timestamp": datetime.utcnow().isoformat(),
            "environment": {
                "mode": env_summary["mode"],
                "variables_status": env_summary["details"],
                "summary": {
                    "total": env_summary["total_vars"],
                    "configured": env_summary["present"],
                    "missing_critical": env_summary["missing_critical"],
                    "missing_important": env_summary["missing_important"]
                }
            },
            "services": service_details,
            "startup": startup_status,
            "recommendations": _get_health_recommendations(env_summary, service_details)
        }
        
    except Exception as e:
        logger.error(f"Detailed health check failed: {e}")
        return {
            "status": "error",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e),
            "message": "Detailed health check system failure"
        }

def _get_health_recommendations(env_summary: dict, service_details: dict) -> list:
    """Generate actionable recommendations based on health status"""
    recommendations = []
    
    if env_summary["missing_critical"] > 0:
        recommendations.append("Set missing critical environment variables to enable full functionality")
    
    if env_summary["missing_important"] > 0:
        recommendations.append("Set missing important environment variables to avoid degraded performance")
    
    for service, details in service_details.items():
        if details["status"] == "unhealthy":
            if service == "database":
                recommendations.append("Check DATABASE_URL and ensure PostgreSQL is accessible")
            elif service == "redis":
                recommendations.append("Check REDIS_URL and ensure Redis is running")
            elif service == "firebase":
                recommendations.append("Verify Firebase credentials and project configuration")
    
    if not recommendations:
        recommendations.append("All systems are operating normally")
    
    return recommendations

@app.get("/debug/firebase")
def debug_firebase():
    """Debug Firebase initialization status"""
    try:
        from . import firebase_auth
        
        firebase_status = {
            "firebase_initialized": hasattr(firebase_auth, 'auth') and firebase_auth.auth is not None,
            "environment": settings.environment,
            "firebase_project_id": settings.firebase_project_id if hasattr(settings, 'firebase_project_id') else "NOT_SET",
            "firebase_client_email": settings.firebase_client_email[:20] + "..." if hasattr(settings, 'firebase_client_email') and settings.firebase_client_email else "NOT_SET",
            "firebase_private_key_set": bool(settings.firebase_private_key) if hasattr(settings, 'firebase_private_key') else False,
            "firebase_client_id": settings.firebase_client_id if hasattr(settings, 'firebase_client_id') else "NOT_SET",
            "firebase_private_key_id": settings.firebase_private_key_id if hasattr(settings, 'firebase_private_key_id') else "NOT_SET"
        }
        
        try:
            test_token = firebase_auth.create_custom_token("test_uid", {"test": "claim"})
            firebase_status["can_create_custom_token"] = True
        except Exception as e:
            firebase_status["can_create_custom_token"] = False
            firebase_status["custom_token_error"] = str(e)
        
        return firebase_status
    except Exception as e:
        return {"error": str(e), "firebase_initialized": False}


@app.get("/health/environment")
def environment_health():
    """Environment-specific health check endpoint"""
    try:
        from .env_validator import env_validator
        
        env_summary = env_validator.get_status_summary()
        
        # Get safe environment info (no sensitive values)
        safe_env_status = {}
        for var_name, result in env_summary["details"].items():
            safe_env_status[var_name] = {
                "status": result["status"],
                "category": result["category"],
                "has_fallback": result.get("has_fallback", False),
                "description": result["description"]
            }
        
        return {
            "environment_mode": env_summary["mode"],
            "can_start_safely": env_summary["can_start"],
            "configuration_percentage": round(env_summary["percentage_configured"], 1),
            "summary": {
                "total_variables": env_summary["total_vars"],
                "configured": env_summary["present"],
                "missing_critical": env_summary["missing_critical"],
                "missing_important": env_summary["missing_important"]
            },
            "variables": safe_env_status,
            "last_validated": env_summary["timestamp"]
        }
    except Exception as e:
        logger.error(f"Environment health check failed: {e}")
        return {
            "status": "error",
            "error": str(e),
            "message": "Environment health check failed"
        }

@app.get("/health/database")
def database_health():
    """Database-specific health check with connection pool status"""
    try:
        from .database_manager import db_manager
        
        connection_status = db_manager.get_connection_status()
        
        # Test actual query performance
        query_start = datetime.utcnow()
        try:
            with db_manager.get_db_session() as session:
                session.execute(text("SELECT 1 as test, NOW() as timestamp"))
                query_time = (datetime.utcnow() - query_start).total_seconds()
                query_success = True
        except Exception as e:
            query_time = (datetime.utcnow() - query_start).total_seconds()
            query_success = False
            query_error = str(e)
        
        response = {
            "database_status": connection_status["status"],
            "healthy": connection_status["healthy"],
            "query_test": {
                "success": query_success,
                "response_time_seconds": round(query_time, 3)
            },
            "connection_pool": connection_status["pool_info"],
            "database_type": connection_status["database_url_type"],
            "last_health_check": connection_status["last_check"]
        }
        
        if not query_success:
            response["query_test"]["error"] = query_error
        
        return response
        
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {
            "database_status": "error",
            "healthy": False,
            "error": str(e),
            "message": "Database health check system failure"
        }

@app.get("/health/jobs")
def job_health():
    """Job queue and background task health check"""
    try:
        from .job_manager import job_manager
        
        health_status = job_manager.get_health_status()
        
        return {
            "job_manager_status": health_status["status"],
            "redis_connected": health_status["redis_connected"],
            "celery_configured": health_status["celery_configured"],
            "job_statistics": health_status["statistics"],
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Job health check failed: {e}")
        return {
            "job_manager_status": "error",
            "error": str(e),
            "message": "Job health check system failure"
        }



class UserRegistrationRequest(BaseModel):
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None


class OAuthCallbackRequest(BaseModel):
    authorization_code: str
    redirect_uri: str


@app.get("/auth/oauth/config")
def get_oauth_config():
    """Get OAuth configuration for frontend"""
    return {
        "google_client_id": settings.google_client_id
    }


@app.post("/auth/oauth/callback")
def handle_oauth_callback(
    request: OAuthCallbackRequest,
    db: Session = Depends(get_db)
):
    """Handle OAuth callback and exchange authorization code for tokens"""
    try:
        logger.info(f"OAuth callback received: code={request.authorization_code[:20]}..., redirect_uri={request.redirect_uri}")
        
        if request.authorization_code in processed_auth_codes:
            logger.warning(f"Authorization code already processed, rejecting duplicate request")
            raise HTTPException(
                status_code=400,
                detail="Authorization code has already been used"
            )
        
        processed_auth_codes.add(request.authorization_code)
        
        # Write callback info to debug file
        with open("oauth_debug.txt", "w") as f:
            f.write(f"OAuth callback started\n")
            f.write(f"Authorization code: {request.authorization_code[:20]}...\n")
            f.write(f"Redirect URI: {request.redirect_uri}\n")
        token_url = "https://oauth2.googleapis.com/token"
        token_data = {
            "code": request.authorization_code,
            "client_id": settings.google_client_id,
            "client_secret": settings.google_client_secret,
            "redirect_uri": request.redirect_uri,
            "grant_type": "authorization_code",
        }
        
        token_response = requests.post(token_url, data=token_data)
        
        if not token_response.ok:
            error_details = token_response.text
            logger.error(f"Token exchange failed: {token_response.status_code} - {error_details}")
            logger.error(f"Request data was: {token_data}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to exchange authorization code: {error_details}"
            )
        
        token_json = token_response.json()
        google_access_token = token_json.get("access_token")
        google_refresh_token = token_json.get("refresh_token")
        id_token = token_json.get("id_token")
        
        if not google_access_token or not id_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing required tokens from Google OAuth response"
            )
        
        try:
            logger.info("Starting ID token verification...")
            logger.info(f"ID token (first 50 chars): {id_token[:50]}...")
            logger.info(f"Google client ID: {settings.google_client_id}")
            
            jwks_client = PyJWKClient("https://www.googleapis.com/oauth2/v3/certs")
            signing_key = jwks_client.get_signing_key_from_jwt(id_token)
            logger.info("Successfully retrieved signing key from JWKS")
            
            decoded_token = jwt.decode(
                id_token,
                signing_key.key,
                algorithms=["RS256"],
                audience=settings.google_client_id,
                options={"verify_iss": False},  # Temporarily disable issuer verification
                leeway=300  # Increase leeway to 5 minutes
            )
            logger.info(f"ID token verification successful. Token payload: {decoded_token}")
            
            token_issuer = decoded_token.get("iss")
            valid_issuers = ["https://accounts.google.com", "accounts.google.com"]
            if token_issuer not in valid_issuers:
                logger.warning(f"Unexpected issuer: {token_issuer}, but continuing...")
            
            logger.info("ID token verification completed successfully")
            
            google_user_id = decoded_token["sub"]
            email = decoded_token.get("email")
            display_name = decoded_token.get("name")
            photo_url = decoded_token.get("picture")
            email_verified = decoded_token.get("email_verified", False)
            
            # Debug: Log what we got from the ID token
            logger.info(f"ID token contents: sub={google_user_id}, email={email}, name={display_name}, email_verified={email_verified}")
            logger.info(f"Full decoded token keys: {list(decoded_token.keys())}")
            
            # Write debug info to file for inspection
            with open("oauth_debug.txt", "w") as f:
                f.write(f"ID token contents:\n")
                f.write(f"sub={google_user_id}\n")
                f.write(f"email={email}\n")
                f.write(f"name={display_name}\n")
                f.write(f"email_verified={email_verified}\n")
                f.write(f"All token keys: {list(decoded_token.keys())}\n")
                f.write(f"Full token: {decoded_token}\n")
            
            # Create a proper Firebase UID - Firebase UIDs should be strings up to 128 chars
            # Using a prefix to ensure it's treated as a string, not a number
            firebase_uid = f"google_{google_user_id}"
            
            if not email:
                logger.error(f"No email found in ID token. Token contents: {decoded_token}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User email is required but not found in Google OAuth response"
                )
            
            # Check for all possible UID formats for backward compatibility
            existing_user = db.query(User).filter(
                (User.firebase_uid == firebase_uid) | 
                (User.firebase_uid == f"google:{google_user_id}") |
                (User.firebase_uid == google_user_id) |
                (User.email == email)
            ).first()
            
            if existing_user:
                existing_user.firebase_uid = firebase_uid
                existing_user.email = email
                existing_user.display_name = display_name or existing_user.display_name
                existing_user.photo_url = photo_url or existing_user.photo_url
                existing_user.set_google_tokens(
                    access_token=google_access_token,
                    refresh_token=google_refresh_token
                )
                db.commit()
                db.refresh(existing_user)
                user = existing_user
                logger.info(f"Updated existing user {user.id} with Firebase UID {firebase_uid}")
            else:
                new_user = User(
                    firebase_uid=firebase_uid,
                    email=email,
                    display_name=display_name,
                    photo_url=photo_url
                )
                new_user.set_google_tokens(
                    access_token=google_access_token,
                    refresh_token=google_refresh_token
                )
                db.add(new_user)
                db.commit()
                db.refresh(new_user)
                user = new_user
                logger.info(f"Registered new user {user.id} with Firebase UID {firebase_uid}")
            
            # Create custom token with email claim
            logger.info(f"About to create Firebase custom token for UID: {firebase_uid}")
            additional_claims = {
                "email": email,
                "name": display_name,
                "picture": photo_url,
                "email_verified": email_verified
            }
            logger.info(f"Additional claims: {additional_claims}")
            
            try:
                logger.info("Attempting to create Firebase custom token...")
                logger.info(f"Firebase UID: {firebase_uid}")
                logger.info(f"Additional claims: {additional_claims}")
                
                from . import firebase_auth
                logger.info(f"Firebase initialized: {firebase_auth._firebase_initialized}")
                
                firebase_custom_token = firebase_auth.create_custom_token(firebase_uid, additional_claims)
                logger.info("Firebase custom token created successfully")
                logger.info(f"Custom token type: {type(firebase_custom_token)}")
                logger.info(f"Custom token length: {len(firebase_custom_token)}")
                logger.info(f"Custom token preview: {firebase_custom_token[:100]}...")
                
                # Log the UID and project info for debugging
                logger.info(f"Firebase UID used: {firebase_uid}")
                logger.info(f"Firebase project ID: {settings.firebase_project_id}")
                
                # Test the token creation process
                try:
                    # Decode without verification to see the token structure
                    decoded_custom = jwt.decode(firebase_custom_token, options={"verify_signature": False})
                    logger.info(f"Custom token contents: {decoded_custom}")
                except Exception as decode_error:
                    logger.error(f"Could not decode custom token: {decode_error}")
            except Exception as e:
                logger.error(f"Firebase custom token creation failed: {e}")
                logger.error(f"Exception type: {type(e).__name__}")
                logger.error(f"Exception args: {e.args}")
                
                try:
                    from . import firebase_auth
                    import firebase_admin
                    logger.error(f"Firebase initialized status: {firebase_auth._firebase_initialized}")
                    logger.error(f"Firebase apps: {len(firebase_admin._apps) if hasattr(firebase_admin, '_apps') else 'unknown'}")
                except Exception as debug_e:
                    logger.error(f"Could not get Firebase debug info: {debug_e}")
                
                raise
            
            # Instead of custom token, return the user data with a session token
            # The frontend will handle authentication differently
            return {
                "firebase_uid": firebase_uid,
                "google_id_token": id_token,  # Send the Google ID token
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "display_name": user.display_name,
                    "photo_url": user.photo_url,
                    "email_verified": email_verified,
                    "firebase_uid": firebase_uid
                }
            }
            
        except jwt.ExpiredSignatureError as e:
            logger.error(f"Google ID token expired: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Google ID token has expired. Please try logging in again."
            )
        except jwt.InvalidAudienceError as e:
            logger.error(f"Invalid audience in Google ID token: {e}")
            logger.error(f"Expected audience: {settings.google_client_id}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Google ID token audience"
            )
        except jwt.InvalidIssuerError as e:
            logger.error(f"Invalid issuer in Google ID token: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Google ID token issuer"
            )
        except Exception as e:
            logger.error(f"Firebase token verification failed: {e}")
            logger.error(f"Exception type: {type(e)}")
            logger.error(f"Token type: {type(id_token)}, Token length: {len(id_token) if id_token else 0}")
            logger.error(f"Token preview: {id_token[:50] if id_token else 'None'}...")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Google ID token"
            )
        
    except requests.RequestException as e:
        logger.error(f"OAuth token exchange request failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to communicate with Google OAuth servers"
        )
    except HTTPException:
        processed_auth_codes.discard(request.authorization_code)
        raise
    except Exception as e:
        processed_auth_codes.discard(request.authorization_code)
        logger.error(f"OAuth callback handling failed: {e}")
        logger.error(f"Exception type: {type(e).__name__}")
        logger.error(f"Exception args: {e.args}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OAuth callback handling failed: {str(e)}"
        )


@app.post("/auth/register")
def register_user(
    request: UserRegistrationRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Register a new user after Firebase authentication with OAuth tokens"""
    try:
        decoded_token = verify_firebase_token(credentials.credentials)
        firebase_uid = decoded_token["uid"]
        email = decoded_token.get("email")
        display_name = decoded_token.get("name")
        photo_url = decoded_token.get("picture")
        email_verified = decoded_token.get("email_verified", False)
        
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User email is required"
            )
        
        if not email_verified:
            logger.warning(f"User {firebase_uid} has unverified email: {email}")
        
        existing_user = db.query(User).filter(User.firebase_uid == firebase_uid).first()
        
        if existing_user:
            if request.access_token or request.refresh_token:
                existing_user.set_google_tokens(
                    access_token=request.access_token,
                    refresh_token=request.refresh_token
                )
            db.commit()
            db.refresh(existing_user)
            
            return {
                "message": "User tokens updated successfully",
                "user_id": existing_user.id,
                "email_verified": email_verified
            }
        
        new_user = User(
            firebase_uid=firebase_uid,
            email=email,
            display_name=display_name,
            photo_url=photo_url
        )
        
        if request.access_token or request.refresh_token:
            new_user.set_google_tokens(
                access_token=request.access_token,
                refresh_token=request.refresh_token
            )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        logger.info(f"Registered new user {new_user.id} with Firebase UID {firebase_uid}")
        
        return {
            "message": "User registered successfully",
            "user_id": new_user.id,
            "email_verified": email_verified
        }
        
    except ValueError as e:
        logger.error(f"Token verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token"
        )
    except Exception as e:
        logger.error(f"Registration failed for token: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed. Please try again."
        )


@app.post("/auth/revoke")
def revoke_user_tokens(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Revoke user tokens on logout"""
    try:
        decoded_token = verify_firebase_token(credentials.credentials)
        firebase_uid = decoded_token["uid"]
        
        user = db.query(User).filter(User.firebase_uid == firebase_uid).first()
        if user:
            user.clear_google_tokens()
            db.commit()
            
            logger.info(f"Revoked tokens for user {user.id}")
        
        return {"message": "Tokens revoked successfully"}
        
    except ValueError as e:
        logger.error(f"Token verification failed during revocation: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token"
        )
    except Exception as e:
        logger.error(f"Token revocation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token revocation failed"
        )


@app.get("/auth/me")
def get_current_user_info(current_user: User = Depends(get_current_firebase_user)):
    """Get current user information"""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "display_name": current_user.display_name,
        "photo_url": current_user.photo_url,
        "youtube_channel_id": current_user.youtube_channel_id,
        "youtube_channel_title": current_user.youtube_channel_title,
        "created_at": current_user.created_at
    }


@app.get("/protected")
def protected_route(current_user: User = Depends(get_current_firebase_user)):
    """Example protected route"""
    return {
        "message": f"Hello {current_user.display_name}!",
        "user_id": current_user.id
    }
