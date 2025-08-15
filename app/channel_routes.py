from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from .database import get_db
from .models import User
from .models import YouTubeChannel
from .auth_dependencies import get_current_user_session, get_current_paid_user
from .youtube_api import get_youtube_client, YouTubeAPIClient
from .tasks import update_quota_usage
from .oauth_refresh import refresh_google_access_token
from .config import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/channels", tags=["channels"])


@router.get("/test")
async def test_auth(current_user: User = Depends(get_current_user_session)):
	"""Test endpoint to verify authentication is working"""
	return {
		"message": "Authentication successful",
		"user_id": current_user.id,
		"email": current_user.email,
		"has_google_tokens": current_user.google_access_token is not None
	}


@router.get("/", response_model=List[Dict[str, Any]])
async def get_user_channels(
    current_user: User = Depends(get_current_paid_user),
    db: Session = Depends(get_db)
):
    """Get all YouTube channels for the current user"""
    try:
        channels = db.query(YouTubeChannel).filter(
            YouTubeChannel.user_id == current_user.id,
            YouTubeChannel.is_active == True
        ).all()
        
        return [channel.to_dict() for channel in channels]
    
    except Exception as e:
        logger.error(f"Error fetching user channels: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch channels: {str(e)}"
        )


@router.post("/sync")
async def sync_user_channels(
    current_user: User = Depends(get_current_paid_user),
    db: Session = Depends(get_db),
    youtube_client: YouTubeAPIClient = Depends(get_youtube_client)
):
    """Sync user's YouTube channels from Google account"""
    try:
        logger.info(f"Starting channel sync for user {current_user.id}")
        
        # TEMPORARY: For testing purposes, return mock data if no valid OAuth tokens
        # This allows endpoint testing without full OAuth flow completion
        access_token = current_user.get_google_access_token()
        has_valid_token = access_token and not current_user.is_token_expired()
        
        if not has_valid_token:
            logger.warning(f"No valid access token for user {current_user.id} ({current_user.email}) - token: {bool(access_token)}, expired: {current_user.is_token_expired()}")
            
            # Check if this is a testing scenario or authorized user
            authorized_emails = [
                "liftedkulture@gmail.com", 
                "liftedkulture-6202@pages.plusgoogle.com",
                "Shemeka.womenofexcellence@gmail.com"
            ]
            logger.info(f"DEBUG: Environment is_development={settings.is_development}, user_email={current_user.email}, authorized_emails={authorized_emails}")
            logger.info(f"DEBUG: User in authorized emails: {current_user.email in authorized_emails}")
            
            # NO MOCK DATA - Force real OAuth completion for authorized users
            logger.info(f"User {current_user.email} needs valid OAuth tokens for real YouTube integration")
            
            if current_user.needs_token_refresh():
                logger.info(f"Attempting token refresh for user {current_user.id}")
                refresh_token = current_user.get_google_refresh_token()
                if refresh_token:
                    new_access_token = await refresh_google_access_token(current_user, db)
                    if new_access_token:
                        access_token = new_access_token
                        logger.info(f"Successfully refreshed access token for user {current_user.id}")
                    else:
                        raise HTTPException(
                            status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Failed to refresh access token. Please re-authenticate with Google."
                        )
                else:
                    logger.error(f"No refresh token available for user {current_user.id}")
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="No refresh token available. Please re-authenticate with Google."
                    )
            else:
                logger.error(f"No valid Google access token for user {current_user.id}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="No valid Google access token. Please re-authenticate with Google."
                )
        
        logger.debug(f"Fetching channel info for user {current_user.id}")
        channel_info = await youtube_client.get_channel_info(access_token)
        logger.info(f"Successfully fetched channel info for user {current_user.id}: {channel_info.get('title', 'Unknown')}")
        
        existing_channel = db.query(YouTubeChannel).filter(
            YouTubeChannel.user_id == current_user.id,
            YouTubeChannel.channel_id == channel_info["id"]
        ).first()
        
        if existing_channel:
            existing_channel.channel_title = channel_info["title"]
            existing_channel.channel_description = channel_info.get("description", "")
            existing_channel.subscriber_count = channel_info.get("subscriber_count", 0)
            existing_channel.video_count = channel_info.get("video_count", 0)
            existing_channel.view_count = channel_info.get("view_count", 0)
            existing_channel.thumbnail_url = channel_info.get("thumbnail_url")
            existing_channel.custom_url = channel_info.get("custom_url")
        else:
            new_channel = YouTubeChannel(
                user_id=current_user.id,
                channel_id=channel_info["id"],
                channel_title=channel_info["title"],
                channel_description=channel_info.get("description", ""),
                subscriber_count=channel_info.get("subscriber_count", 0),
                video_count=channel_info.get("video_count", 0),
                view_count=channel_info.get("view_count", 0),
                thumbnail_url=channel_info.get("thumbnail_url"),
                custom_url=channel_info.get("custom_url"),
                is_selected=True  # Auto-select if it's the first/only channel
            )
            db.add(new_channel)
        
        current_user.youtube_channel_id = channel_info["id"]
        current_user.youtube_channel_title = channel_info["title"]
        
        db.commit()
        
        # update_quota_usage.delay(current_user.id, "videos_list", 1)  # Disabled - TODO: Setup Redis
        
        channels = db.query(YouTubeChannel).filter(
            YouTubeChannel.user_id == current_user.id,
            YouTubeChannel.is_active == True
        ).all()
        
        return [channel.to_dict() for channel in channels]
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error syncing user channels for user {current_user.id}: {str(e)}", exc_info=True)
        
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
                detail=f"Failed to sync channels: {str(e)}. Please try again or re-authenticate with Google."
            )


@router.post("/{channel_id}/select")
async def select_channel(
    channel_id: str,
    current_user: User = Depends(get_current_paid_user),
    db: Session = Depends(get_db)
):
    """Select a specific YouTube channel as active"""
    try:
        db.query(YouTubeChannel).filter(
            YouTubeChannel.user_id == current_user.id
        ).update({"is_selected": False})
        
        channel = db.query(YouTubeChannel).filter(
            YouTubeChannel.user_id == current_user.id,
            YouTubeChannel.channel_id == channel_id
        ).first()
        
        if not channel:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Channel not found"
            )
        
        channel.is_selected = True
        
        current_user.youtube_channel_id = channel.channel_id
        current_user.youtube_channel_title = channel.channel_title
        
        db.commit()
        
        return {"message": "Channel selected successfully", "channel": channel.to_dict()}
    
    except Exception as e:
        db.rollback()
        logger.error(f"Error selecting channel: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to select channel"
        )


@router.get("/selected")
async def get_selected_channel(
    current_user: User = Depends(get_current_paid_user),
    db: Session = Depends(get_db)
):
    """Get the currently selected YouTube channel"""
    try:
        selected_channel = db.query(YouTubeChannel).filter(
            YouTubeChannel.user_id == current_user.id,
            YouTubeChannel.is_selected == True
        ).first()
        
        if not selected_channel:
            return None
        
        return selected_channel.to_dict()
    
    except Exception as e:
        logger.error(f"Error fetching selected channel: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch selected channel"
        )
