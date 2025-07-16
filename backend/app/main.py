from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from .config import settings
from .database import get_db
from .firebase_auth import verify_firebase_token
from .models import User
from .ab_test_routes import router as ab_test_router, get_current_user
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
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ab_test_router)

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


@app.post("/auth/register")
def register_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Register a new user after Firebase authentication"""
    try:
        decoded_token = verify_firebase_token(credentials.credentials)
        firebase_uid = decoded_token["uid"]
        email = decoded_token.get("email")
        display_name = decoded_token.get("name")
        photo_url = decoded_token.get("picture")
        
        existing_user = db.query(User).filter(User.firebase_uid == firebase_uid).first()
        
        if existing_user:
            return {"message": "User already registered", "user_id": existing_user.id}
        
        new_user = User(
            firebase_uid=firebase_uid,
            email=email,
            display_name=display_name,
            photo_url=photo_url
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return {
            "message": "User registered successfully",
            "user_id": new_user.id
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
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
