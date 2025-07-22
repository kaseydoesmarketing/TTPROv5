from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from .config import settings
from .database import get_db
from .firebase_auth import verify_firebase_token
from .models import User
from .ab_test_routes import router as ab_test_router
from .channel_routes import router as channel_router, get_current_user
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="TitleTesterPro API",
    description="A SaaS platform for A/B testing YouTube titles",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)

app.include_router(ab_test_router)
app.include_router(channel_router)

security = HTTPBearer()


@app.get("/")
def read_root():
    return {
        "message": "TitleTesterPro API",
        "version": "1.0.0",
        "status": "healthy"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/healthz")
async def healthz():
    return {"status": "ok"}


class UserRegistrationRequest(BaseModel):
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None


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
def get_current_user_info(current_user: User = Depends(get_current_user)):
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
def protected_route(current_user: User = Depends(get_current_user)):
    """Example protected route"""
    return {
        "message": f"Hello {current_user.display_name}!",
        "user_id": current_user.id
    }
