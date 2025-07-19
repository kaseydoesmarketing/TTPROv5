from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, Field

from .database import get_db
from .models import User, ABTest, TitleRotation, QuotaUsage
from .youtube_api import get_youtube_client, YouTubeAPIClient
from .firebase_auth import verify_firebase_token
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/ab-tests", tags=["A/B Tests"])
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Get current authenticated user from Firebase token - production only, no fallbacks"""
    try:
        if not credentials or not credentials.credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication token is required"
            )
        
        decoded_token = verify_firebase_token(credentials.credentials)
        firebase_uid = decoded_token["uid"]
        email = decoded_token.get("email")
        
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User email is required"
            )
        
        user = db.query(User).filter(User.firebase_uid == firebase_uid).first()
        
        if not user:
            logger.warning(f"User not found in database for Firebase UID: {firebase_uid}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found. Please complete registration first."
            )
        
        logger.debug(f"Authenticated user {user.id} ({user.email})")
        return user
        
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Token verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token"
        )
    except Exception as e:
        logger.error(f"Authentication failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication failed"
        )


class CreateABTestRequest(BaseModel):
    video_id: str = Field(..., description="YouTube video ID")
    title_variants: List[str] = Field(..., min_items=2, max_items=5, description="List of title variants to test")
    test_duration_hours: int = Field(default=24, ge=1, le=168, description="Test duration in hours (1-168)")
    rotation_interval_hours: int = Field(default=4, ge=1, le=24, description="Title rotation interval in hours (1-24)")


class ABTestResponse(BaseModel):
    id: str
    video_id: str
    video_title: str
    title_variants: List[str]
    current_variant_index: int
    test_duration_hours: int
    rotation_interval_hours: int
    status: str
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]


class TitleRotationResponse(BaseModel):
    id: str
    variant_index: int
    title: str
    started_at: datetime
    ended_at: Optional[datetime]
    views: Optional[int] = 0
    impressions: Optional[int] = 0
    ctr: Optional[float] = 0.0


@router.post("/", response_model=ABTestResponse)
async def create_ab_test(
    request: CreateABTestRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    youtube_client: YouTubeAPIClient = Depends(get_youtube_client)
):
    """Create a new A/B test for a YouTube video"""
    try:
        video_details = await youtube_client.get_video_details(request.video_id)
        if not video_details:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Video not found"
            )
        
        existing_test = db.query(ABTest).filter(
            ABTest.user_id == current_user.id,
            ABTest.video_id == request.video_id,
            ABTest.status.in_(["draft", "active"])
        ).first()
        
        if existing_test:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="An active test already exists for this video"
            )
        
        ab_test = ABTest(
            user_id=current_user.id,
            video_id=request.video_id,
            video_title=video_details["title"],
            title_variants=request.title_variants,
            test_duration_hours=request.test_duration_hours,
            rotation_interval_hours=request.rotation_interval_hours,
            current_variant_index=0,
            status="draft"
        )
        
        db.add(ab_test)
        db.commit()
        db.refresh(ab_test)
        
        logger.info(f"Created A/B test {ab_test.id} for user {current_user.id}")
        
        return ABTestResponse(
            id=ab_test.id,
            video_id=ab_test.video_id,
            video_title=ab_test.video_title,
            title_variants=ab_test.title_variants,
            current_variant_index=ab_test.current_variant_index,
            test_duration_hours=ab_test.test_duration_hours,
            rotation_interval_hours=ab_test.rotation_interval_hours,
            status=ab_test.status,
            created_at=ab_test.created_at,
            started_at=ab_test.started_at,
            completed_at=ab_test.completed_at
        )
        
    except Exception as e:
        logger.error(f"Error creating A/B test: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create A/B test"
        )


@router.get("/", response_model=List[ABTestResponse])
async def get_user_ab_tests(
    status_filter: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all A/B tests for the current user"""
    query = db.query(ABTest).filter(ABTest.user_id == current_user.id)
    
    if status_filter:
        query = query.filter(ABTest.status == status_filter)
    
    tests = query.order_by(ABTest.created_at.desc()).all()
    
    return [
        ABTestResponse(
            id=test.id,
            video_id=test.video_id,
            video_title=test.video_title,
            title_variants=test.title_variants,
            current_variant_index=test.current_variant_index,
            test_duration_hours=test.test_duration_hours,
            rotation_interval_hours=test.rotation_interval_hours,
            status=test.status,
            created_at=test.created_at,
            started_at=test.started_at,
            completed_at=test.completed_at
        )
        for test in tests
    ]


@router.get("/{test_id}", response_model=ABTestResponse)
async def get_ab_test(
    test_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific A/B test"""
    test = db.query(ABTest).filter(
        ABTest.id == test_id,
        ABTest.user_id == current_user.id
    ).first()
    
    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="A/B test not found"
        )
    
    return ABTestResponse(
        id=test.id,
        video_id=test.video_id,
        video_title=test.video_title,
        title_variants=test.title_variants,
        current_variant_index=test.current_variant_index,
        test_duration_hours=test.test_duration_hours,
        rotation_interval_hours=test.rotation_interval_hours,
        status=test.status,
        created_at=test.created_at,
        started_at=test.started_at,
        completed_at=test.completed_at
    )


@router.post("/{test_id}/start")
async def start_ab_test(
    test_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    youtube_client: YouTubeAPIClient = Depends(get_youtube_client)
):
    """Start an A/B test"""
    test = db.query(ABTest).filter(
        ABTest.id == test_id,
        ABTest.user_id == current_user.id,
        ABTest.status == "draft"
    ).first()
    
    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="A/B test not found or already started"
        )
    
    try:
        first_title = test.title_variants[0]
        
        if not current_user.google_access_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="YouTube access token not available. Please re-authenticate with Google."
            )
        
        success = await youtube_client.update_video_title(
            test.video_id,
            first_title,
            current_user.google_access_token
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update video title on YouTube"
            )
        
        test.status = "active"
        test.started_at = datetime.utcnow()
        test.current_variant_index = 0
        
        rotation = TitleRotation(
            ab_test_id=test.id,
            variant_index=0,
            title=first_title,
            started_at=datetime.utcnow()
        )
        
        db.add(rotation)
        db.commit()
        
        logger.info(f"Started A/B test {test.id}")
        
        return {"message": "A/B test started successfully"}
        
    except Exception as e:
        logger.error(f"Error starting A/B test: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start A/B test"
        )


@router.post("/{test_id}/stop")
async def stop_ab_test(
    test_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Stop an active A/B test"""
    test = db.query(ABTest).filter(
        ABTest.id == test_id,
        ABTest.user_id == current_user.id,
        ABTest.status == "active"
    ).first()
    
    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Active A/B test not found"
        )
    
    try:
        test.status = "stopped"
        test.completed_at = datetime.utcnow()
        
        current_rotation = db.query(TitleRotation).filter(
            TitleRotation.ab_test_id == test.id,
            TitleRotation.ended_at.is_(None)
        ).first()
        
        if current_rotation:
            current_rotation.ended_at = datetime.utcnow()
        
        db.commit()
        
        logger.info(f"Stopped A/B test {test.id}")
        
        return {"message": "A/B test stopped successfully"}
        
    except Exception as e:
        logger.error(f"Error stopping A/B test: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to stop A/B test"
        )


@router.get("/{test_id}/rotations", response_model=List[TitleRotationResponse])
async def get_test_rotations(
    test_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get rotation history for an A/B test"""
    test = db.query(ABTest).filter(
        ABTest.id == test_id,
        ABTest.user_id == current_user.id
    ).first()
    
    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="A/B test not found"
        )
    
    rotations = db.query(TitleRotation).filter(
        TitleRotation.ab_test_id == test_id
    ).order_by(TitleRotation.started_at.asc()).all()
    
    return [
        TitleRotationResponse(
            id=rotation.id,
            variant_index=rotation.variant_index,
            title=rotation.title,
            started_at=rotation.started_at,
            ended_at=rotation.ended_at,
            views=rotation.views or 0,
            impressions=rotation.impressions or 0,
            ctr=rotation.ctr or 0.0
        )
        for rotation in rotations
    ]


@router.delete("/{test_id}")
async def delete_ab_test(
    test_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an A/B test (only if not active)"""
    test = db.query(ABTest).filter(
        ABTest.id == test_id,
        ABTest.user_id == current_user.id
    ).first()
    
    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="A/B test not found"
        )
    
    if test.status == "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete an active test. Stop the test first."
        )
    
    try:
        db.query(TitleRotation).filter(TitleRotation.ab_test_id == test_id).delete()
        
        db.delete(test)
        db.commit()
        
        logger.info(f"Deleted A/B test {test_id}")
        
        return {"message": "A/B test deleted successfully"}
        
    except Exception as e:
        logger.error(f"Error deleting A/B test: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete A/B test"
        )
