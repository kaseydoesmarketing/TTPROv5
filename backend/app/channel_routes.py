from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from .database import get_db
from .models import User
from .models import YouTubeChannel
from .firebase_auth import verify_firebase_token
from .youtube_api import get_youtube_client, YouTubeAPIClient
from .tasks import update_quota_usage
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/channels", tags=["channels"])


async def get_current_user(
    token: dict = Depends(verify_firebase_token),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    user = db.query(User).filter(User.firebase_uid == token["uid"]).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.get("/", response_model=List[Dict[str, Any]])
async def get_user_channels(
    current_user: User = Depends(get_current_user),
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
            detail="Failed to fetch channels"
        )


@router.post("/sync")
async def sync_user_channels(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    youtube_client: YouTubeAPIClient = Depends(get_youtube_client)
):
    """Sync user's YouTube channels from Google account"""
    try:
        access_token = current_user.get_google_access_token()
        if not access_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No valid Google access token"
            )
        
        channel_info = await youtube_client.get_channel_info(access_token)
        
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
        
        update_quota_usage.delay(current_user.id, "videos_list", 1)
        
        channels = db.query(YouTubeChannel).filter(
            YouTubeChannel.user_id == current_user.id,
            YouTubeChannel.is_active == True
        ).all()
        
        return [channel.to_dict() for channel in channels]
    
    except Exception as e:
        db.rollback()
        logger.error(f"Error syncing user channels: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to sync channels"
        )


@router.post("/{channel_id}/select")
async def select_channel(
    channel_id: str,
    current_user: User = Depends(get_current_user),
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
    current_user: User = Depends(get_current_user),
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
