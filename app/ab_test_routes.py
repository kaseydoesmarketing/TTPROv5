from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel, Field

from .database import get_db
from .models import User, ABTest, TitleRotation, QuotaUsage
from .youtube_api import get_youtube_client, YouTubeAPIClient
from .auth_dependencies import get_current_paid_user
from .tasks import update_quota_usage
from .services.token_refresh import refresh_google_token
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/ab-tests", tags=["A/B Tests"])


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
    current_user: User = Depends(get_current_paid_user),
    db: Session = Depends(get_db),
    youtube_client: YouTubeAPIClient = Depends(get_youtube_client)
):
    """Create a new A/B test for a YouTube video"""
    try:
        from .config import settings
        
        # Development mode: use mock video details
        if settings.environment.lower() == "development":
            logger.info("Development mode: using mock video details for test creation")
            mock_videos = {
                "mock_video_1": "How to Optimize YouTube Titles for Maximum Views",
                "mock_video_2": "Advanced YouTube Marketing Strategies That Actually Work", 
                "mock_video_3": "YouTube Analytics Deep Dive - Track Your Success Like a Pro",
                "mock_video_4": "The Ultimate Guide to YouTube SEO in 2024",
                "mock_video_5": "Content Creator Secrets: How I Grew to 100K Subscribers"
            }
            
            video_details = {
                "title": mock_videos.get(request.video_id, "Mock Video Title"),
                "id": request.video_id
            }
        else:
            access_token = current_user.get_google_access_token()
            if not access_token:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="YouTube access token not available. Please re-authenticate with Google."
                )
            
            video_details = await youtube_client.get_video_details(request.video_id, access_token)
            if not video_details:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Video not found"
                )
        
        from .config import settings
        # Temporarily disabled Celery tasks - TODO: Setup Redis
        # if not settings.is_development:
        #     update_quota_usage.delay(current_user.id, "videos_list", 1)
        # else:
        logger.info("Skipping quota usage update - Celery disabled")
        
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
    current_user: User = Depends(get_current_paid_user),
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
    current_user: User = Depends(get_current_paid_user),
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
    current_user: User = Depends(get_current_paid_user),
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
        logger.info(f"Starting A/B test {test.id}: updating video {test.video_id} title to '{first_title}'")
        
        access_token = current_user.get_google_access_token()
        if not access_token:
            logger.error(f"No access token available for user {current_user.id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="YouTube access token not available. Please re-authenticate with Google."
            )
        
        logger.info(f"Attempting to update video title via YouTube API...")
        success = await youtube_client.update_video_title(
            test.video_id,
            first_title,
            access_token
        )
        
        if not success:
            logger.error(f"YouTube API failed to update video title for video {test.video_id}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update video title on YouTube"
            )
        
        logger.info(f"Successfully updated video {test.video_id} title to '{first_title}'")
        
        # update_quota_usage.delay(current_user.id, "videos_update", 50)  # Disabled - TODO: Setup Redis
        
        test.status = "active"
        test.started_at = datetime.now(timezone.utc)
        test.current_variant_index = 0
        
        rotation = TitleRotation(
            ab_test_id=test.id,
            variant_index=0,
            title=first_title,
            started_at=datetime.now(timezone.utc)
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


@router.post("/{test_id}/pause")
async def pause_ab_test(
    test_id: str,
    current_user: User = Depends(get_current_paid_user),
    db: Session = Depends(get_db)
):
    """Pause an active A/B test"""
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
        test.status = "paused"
        
        current_rotation = db.query(TitleRotation).filter(
            TitleRotation.ab_test_id == test.id,
            TitleRotation.ended_at.is_(None)
        ).first()
        
        if current_rotation:
            current_rotation.ended_at = datetime.now(timezone.utc)
        
        db.commit()
        
        logger.info(f"Paused A/B test {test.id}")
        
        return {"message": "A/B test paused successfully"}
        
    except Exception as e:
        logger.error(f"Error pausing A/B test: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to pause A/B test"
        )


@router.post("/{test_id}/resume")
async def resume_ab_test(
    test_id: str,
    current_user: User = Depends(get_current_paid_user),
    db: Session = Depends(get_db)
):
    """Resume a paused A/B test"""
    test = db.query(ABTest).filter(
        ABTest.id == test_id,
        ABTest.user_id == current_user.id,
        ABTest.status == "paused"
    ).first()
    
    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paused A/B test not found"
        )
    
    try:
        test.status = "active"
        
        db.commit()
        
        logger.info(f"Resumed A/B test {test.id}")
        
        return {"message": "A/B test resumed successfully"}
        
    except Exception as e:
        logger.error(f"Error resuming A/B test: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to resume A/B test"
        )


@router.post("/{test_id}/stop")
async def stop_ab_test(
    test_id: str,
    current_user: User = Depends(get_current_paid_user),
    db: Session = Depends(get_db)
):
    """Stop an active or paused A/B test"""
    test = db.query(ABTest).filter(
        ABTest.id == test_id,
        ABTest.user_id == current_user.id,
        ABTest.status.in_(["active", "paused"])
    ).first()
    
    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Active or paused A/B test not found"
        )
    
    try:
        test.status = "stopped"
        test.completed_at = datetime.now(timezone.utc)
        
        current_rotation = db.query(TitleRotation).filter(
            TitleRotation.ab_test_id == test.id,
            TitleRotation.ended_at.is_(None)
        ).first()
        
        if current_rotation:
            current_rotation.ended_at = datetime.now(timezone.utc)
        
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
    current_user: User = Depends(get_current_paid_user),
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


@router.get("/channel/videos")
async def get_channel_videos(
    max_results: int = 50,
    current_user: User = Depends(get_current_paid_user),
    db: Session = Depends(get_db),
    youtube_client: YouTubeAPIClient = Depends(get_youtube_client)
):
    """Get videos from the user's YouTube channel"""
    try:
        from .config import settings
        
        # NO MOCK DATA - Always use real YouTube API in production
        
        logger.info(f"Starting channel videos fetch for user {current_user.id}")
        
        # Bypass token refresh for authorized emails to avoid session issues
        authorized_emails = [
            "liftedkulture@gmail.com", 
            "liftedkulture-6202@pages.plusgoogle.com",
            "Shemeka.womenofexcellence@gmail.com"
        ]
        
        # Check if user needs token refresh or doesn't have a valid token
        access_token = current_user.get_google_access_token()
        logger.info(f"User {current_user.email} current token status: has_token={bool(access_token)}, needs_refresh={current_user.needs_token_refresh()}")
        
        if not access_token or current_user.needs_token_refresh():
            logger.info(f"Token refresh needed for user {current_user.id}")
            
            # For authorized users, attempt refresh but handle failures gracefully
            if current_user.email in authorized_emails:
                logger.info(f"Attempting token refresh for authorized user {current_user.email}")
                try:
                    access_token = refresh_google_token(current_user)
                    logger.info(f"Successfully refreshed token for authorized user {current_user.email}")
                except ValueError as e:
                    logger.error(f"Token refresh failed for authorized user {current_user.email}: {e}")
                    raise HTTPException(
                        status_code=401, 
                        detail="Your Google authentication has expired. Please sign out and sign in again to refresh your YouTube access."
                    )
            else:
                # For non-authorized users, standard token refresh
                try:
                    access_token = refresh_google_token(current_user)
                except ValueError as e:
                    raise HTTPException(status_code=401, detail=str(e))
        else:
            logger.info(f"Using existing valid token for user {current_user.email}")
        
        from .models import YouTubeChannel
        selected_channel = db.query(YouTubeChannel).filter(
            YouTubeChannel.user_id == current_user.id,
            YouTubeChannel.is_selected == True
        ).first()
        
        if selected_channel:
            logger.debug(f"Using selected channel {selected_channel.channel_id} for user {current_user.id}")
            channel_id = selected_channel.channel_id
            channel_info = {
                "id": selected_channel.channel_id,
                "title": selected_channel.channel_title,
                "description": selected_channel.channel_description,
                "thumbnail_url": selected_channel.thumbnail_url
            }
        else:
            logger.debug(f"No selected channel found, fetching channel info for user {current_user.id}")
            channel_info = await youtube_client.get_channel_info(access_token)
            channel_id = channel_info["id"]
            logger.info(f"Fetched channel info for user {current_user.id}: {channel_info.get('title', 'Unknown')}")
        
        logger.info(f"Fetching videos for channel {channel_id}, max_results: {max_results}")
        logger.info(f"Using access token: {access_token[:20]}..." if access_token else "No access token")
        
        videos = await youtube_client.get_channel_videos(channel_id, access_token, max_results)
        logger.info(f"Successfully fetched {len(videos)} videos for user {current_user.id}")
        
        if not videos:
            logger.warning(f"No videos returned for channel {channel_id}. This could indicate:")
            logger.warning("1. Channel has no videos")
            logger.warning("2. Videos are private/unlisted")  
            logger.warning("3. Access token lacks YouTube scope")
            logger.warning("4. YouTube API authentication issue")
        
        from .config import settings
        # Temporarily disabled Celery tasks - TODO: Setup Redis
        # if not settings.is_development:
        #     update_quota_usage.delay(current_user.id, "videos_list", 2)  # 1 for channel info + 1 for videos list
        
        return {
            "channel": channel_info,
            "videos": videos
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching channel videos for user {current_user.id}: {str(e)}", exc_info=True)
        
        if "quota" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="YouTube API quota exceeded. Please try again later."
            )
        elif "forbidden" in str(e).lower() or "permission" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="YouTube API access denied. Please check your Google account permissions."
            )
        elif "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="YouTube channel not found. Please ensure you have a YouTube channel associated with your Google account."
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to fetch channel videos: {str(e)}. Please try again or re-authenticate with Google."
            )


@router.post("/{test_id}/rotate")
async def manual_title_rotation(
    test_id: str,
    current_user: User = Depends(get_current_paid_user),
    db: Session = Depends(get_db),
    youtube_client: YouTubeAPIClient = Depends(get_youtube_client)
):
    """Manually trigger title rotation for an active test"""
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
        # Get next title variant
        next_index = (test.current_variant_index + 1) % len(test.title_variants)
        next_title = test.title_variants[next_index]
        
        # Get access token
        access_token = current_user.get_google_access_token()
        if not access_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="YouTube access token not available"
            )
        
        # Update video title on YouTube
        success = await youtube_client.update_video_title(
            test.video_id,
            next_title,
            access_token
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update video title on YouTube"
            )
        
        # End current rotation
        current_rotation = db.query(TitleRotation).filter(
            TitleRotation.ab_test_id == test.id,
            TitleRotation.ended_at.is_(None)
        ).first()
        
        if current_rotation:
            current_rotation.ended_at = datetime.now(timezone.utc)
        
        # Create new rotation record
        new_rotation = TitleRotation(
            ab_test_id=test.id,
            variant_index=next_index,
            title=next_title,
            started_at=datetime.now(timezone.utc)
        )
        
        # Update test
        test.current_variant_index = next_index
        
        db.add(new_rotation)
        db.commit()
        
        logger.info(f"Manual rotation: Test {test_id} rotated to variant {next_index}: '{next_title}'")
        
        return {
            "message": "Title rotated successfully",
            "new_variant_index": next_index,
            "new_title": next_title
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error in manual rotation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to rotate title"
        )


@router.delete("/{test_id}")
async def delete_ab_test(
    test_id: str,
    current_user: User = Depends(get_current_paid_user),
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
