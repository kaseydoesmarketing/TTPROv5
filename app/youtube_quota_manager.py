"""
YouTube API Quota Management and Rate Limiting
Prevents quota exhaustion and handles API limits gracefully
"""

import logging
import time
import json
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
from functools import wraps
from contextlib import asynccontextmanager

import redis
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials

from .config import settings

logger = logging.getLogger(__name__)

class QuotaLimitType(Enum):
    DAILY = "daily"
    PER_100_SECONDS = "per_100_seconds"
    PER_USER_100_SECONDS = "per_user_100_seconds"

@dataclass
class QuotaLimits:
    """YouTube API quota limits"""
    daily_limit: int = 10000  # Default daily quota
    per_100_seconds_limit: int = 10000  # Per 100 seconds
    per_user_100_seconds_limit: int = 10000  # Per user per 100 seconds

@dataclass
class APICallCosts:
    """Quota costs for different API operations"""
    channels_list: int = 1
    videos_list: int = 1
    videos_update: int = 50
    playlist_items_list: int = 1
    search_list: int = 100
    analytics_query: int = 10

class YouTubeQuotaManager:
    """Manages YouTube API quota usage and rate limiting"""
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.quota_limits = QuotaLimits()
        self.api_costs = APICallCosts()
        self.quota_key_prefix = "yt_quota"
        self.rate_limit_key_prefix = "yt_rate_limit"
        self.connection_healthy = False
        
    def initialize(self) -> bool:
        """Initialize quota manager with Redis"""
        try:
            redis_url = settings.redis_url or "redis://localhost:6379/0"
            self.redis_client = redis.from_url(
                redis_url,
                socket_timeout=5,
                socket_connect_timeout=5,
                retry_on_timeout=True
            )
            
            # Test connection
            self.redis_client.ping()
            self.connection_healthy = True
            
            logger.info("✅ YouTube quota manager initialized")
            return True
            
        except Exception as e:
            logger.error(f"❌ YouTube quota manager initialization failed: {e}")
            self.connection_healthy = False
            return False
    
    def check_quota_available(self, operation: str, user_id: Optional[str] = None, cost_override: Optional[int] = None) -> Dict[str, Any]:
        """Check if quota is available for an operation"""
        try:
            if not self.connection_healthy:
                # If Redis is down, allow operations but log warning
                logger.warning("⚠️ Redis unavailable, allowing operation without quota check")
                return {"allowed": True, "reason": "quota_check_unavailable"}
            
            cost = cost_override or getattr(self.api_costs, operation, 1)
            current_time = datetime.utcnow()
            
            # Check daily quota
            daily_usage = self._get_quota_usage(QuotaLimitType.DAILY)
            if daily_usage + cost > self.quota_limits.daily_limit:
                return {
                    "allowed": False,
                    "reason": "daily_quota_exceeded",
                    "current_usage": daily_usage,
                    "limit": self.quota_limits.daily_limit,
                    "cost": cost
                }
            
            # Check per-100-seconds quota
            per_100s_usage = self._get_quota_usage(QuotaLimitType.PER_100_SECONDS)
            if per_100s_usage + cost > self.quota_limits.per_100_seconds_limit:
                return {
                    "allowed": False,
                    "reason": "rate_limit_exceeded",
                    "current_usage": per_100s_usage,
                    "limit": self.quota_limits.per_100_seconds_limit,
                    "cost": cost,
                    "retry_after": 100  # seconds
                }
            
            # Check per-user per-100-seconds quota (if user_id provided)
            if user_id:
                user_100s_usage = self._get_quota_usage(QuotaLimitType.PER_USER_100_SECONDS, user_id)
                if user_100s_usage + cost > self.quota_limits.per_user_100_seconds_limit:
                    return {
                        "allowed": False,
                        "reason": "user_rate_limit_exceeded",
                        "current_usage": user_100s_usage,
                        "limit": self.quota_limits.per_user_100_seconds_limit,
                        "cost": cost,
                        "retry_after": 100,
                        "user_id": user_id
                    }
            
            return {
                "allowed": True,
                "cost": cost,
                "daily_usage_after": daily_usage + cost,
                "daily_remaining": self.quota_limits.daily_limit - (daily_usage + cost)
            }
            
        except Exception as e:
            logger.error(f"❌ Quota check failed: {e}")
            # Allow operation if quota check fails
            return {"allowed": True, "reason": "quota_check_error", "error": str(e)}
    
    def _get_quota_usage(self, limit_type: QuotaLimitType, user_id: Optional[str] = None) -> int:
        """Get current quota usage for a limit type"""
        try:
            if not self.redis_client or not self.connection_healthy:
                return 0
            
            current_time = datetime.utcnow()
            
            if limit_type == QuotaLimitType.DAILY:
                key = f"{self.quota_key_prefix}:daily:{current_time.strftime('%Y-%m-%d')}"
            elif limit_type == QuotaLimitType.PER_100_SECONDS:
                window = int(current_time.timestamp() // 100)
                key = f"{self.rate_limit_key_prefix}:100s:{window}"
            elif limit_type == QuotaLimitType.PER_USER_100_SECONDS:
                if not user_id:
                    return 0
                window = int(current_time.timestamp() // 100)
                key = f"{self.rate_limit_key_prefix}:user:{user_id}:100s:{window}"
            else:
                return 0
            
            usage = self.redis_client.get(key)
            return int(usage) if usage else 0
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to get quota usage: {e}")
            return 0
    
    def record_quota_usage(self, operation: str, user_id: Optional[str] = None, cost_override: Optional[int] = None):
        """Record quota usage for an operation"""
        try:
            if not self.connection_healthy:
                return
            
            cost = cost_override or getattr(self.api_costs, operation, 1)
            current_time = datetime.utcnow()
            
            # Record daily usage
            daily_key = f"{self.quota_key_prefix}:daily:{current_time.strftime('%Y-%m-%d')}"
            self.redis_client.incrby(daily_key, cost)
            self.redis_client.expire(daily_key, 86400)  # Expire at end of day
            
            # Record per-100-seconds usage
            window = int(current_time.timestamp() // 100)
            rate_key = f"{self.rate_limit_key_prefix}:100s:{window}"
            self.redis_client.incrby(rate_key, cost)
            self.redis_client.expire(rate_key, 200)  # Expire after 200 seconds
            
            # Record per-user per-100-seconds usage
            if user_id:
                user_rate_key = f"{self.rate_limit_key_prefix}:user:{user_id}:100s:{window}"
                self.redis_client.incrby(user_rate_key, cost)
                self.redis_client.expire(user_rate_key, 200)
            
            logger.debug(f"📊 Recorded quota usage: {operation} = {cost} units")
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to record quota usage: {e}")
    
    def get_quota_status(self) -> Dict[str, Any]:
        """Get current quota status and usage"""
        try:
            current_time = datetime.utcnow()
            
            daily_usage = self._get_quota_usage(QuotaLimitType.DAILY)
            rate_limit_usage = self._get_quota_usage(QuotaLimitType.PER_100_SECONDS)
            
            daily_percentage = (daily_usage / self.quota_limits.daily_limit) * 100
            
            return {
                "daily": {
                    "used": daily_usage,
                    "limit": self.quota_limits.daily_limit,
                    "remaining": self.quota_limits.daily_limit - daily_usage,
                    "percentage_used": round(daily_percentage, 2)
                },
                "rate_limit_100s": {
                    "used": rate_limit_usage,
                    "limit": self.quota_limits.per_100_seconds_limit,
                    "remaining": self.quota_limits.per_100_seconds_limit - rate_limit_usage
                },
                "status": "healthy" if daily_percentage < 90 else "warning" if daily_percentage < 95 else "critical",
                "timestamp": current_time.isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get quota status: {e}")
            return {"status": "error", "error": str(e)}
    
    def get_estimated_reset_time(self, limit_type: QuotaLimitType) -> Optional[datetime]:
        """Get estimated time when quota/rate limit resets"""
        current_time = datetime.utcnow()
        
        if limit_type == QuotaLimitType.DAILY:
            # Resets at midnight UTC
            tomorrow = current_time.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
            return tomorrow
        elif limit_type in [QuotaLimitType.PER_100_SECONDS, QuotaLimitType.PER_USER_100_SECONDS]:
            # Resets every 100 seconds
            current_window = int(current_time.timestamp() // 100)
            next_window_start = (current_window + 1) * 100
            return datetime.fromtimestamp(next_window_start)
        
        return None

class EnhancedYouTubeAPIClient:
    """Enhanced YouTube API client with quota management and resilience"""
    
    def __init__(self, quota_manager: Optional[YouTubeQuotaManager] = None):
        self.quota_manager = quota_manager or youtube_quota_manager
        self.api_key = settings.youtube_api_key
        
    def _check_and_record_quota(self, operation: str, user_id: Optional[str] = None) -> bool:
        """Check quota availability and record usage"""
        quota_check = self.quota_manager.check_quota_available(operation, user_id)
        
        if not quota_check["allowed"]:
            reason = quota_check["reason"]
            if reason == "daily_quota_exceeded":
                raise QuotaExceededException(
                    f"Daily quota limit exceeded. Used: {quota_check['current_usage']}/{quota_check['limit']}"
                )
            elif reason in ["rate_limit_exceeded", "user_rate_limit_exceeded"]:
                retry_after = quota_check.get("retry_after", 100)
                raise RateLimitExceededException(
                    f"Rate limit exceeded. Retry after {retry_after} seconds"
                )
        
        # Record usage
        self.quota_manager.record_quota_usage(operation, user_id)
        return True
    
    async def get_channel_info_with_quota(self, access_token: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Get channel info with quota management"""
        self._check_and_record_quota("channels_list", user_id)
        
        try:
            credentials = Credentials(token=access_token)
            youtube = build('youtube', 'v3', credentials=credentials)
            
            request = youtube.channels().list(
                part='snippet,statistics',
                mine=True
            )
            response = request.execute()
            
            if not response.get('items'):
                raise ValueError("No channel found for the authenticated user")
            
            channel = response['items'][0]
            snippet = channel.get('snippet', {})
            statistics = channel.get('statistics', {})
            
            return {
                "id": channel['id'],
                "title": snippet.get('title', ''),
                "description": snippet.get('description', ''),
                "subscriber_count": int(statistics.get('subscriberCount', 0)),
                "video_count": int(statistics.get('videoCount', 0)),
                "view_count": int(statistics.get('viewCount', 0))
            }
            
        except HttpError as e:
            self._handle_youtube_api_error(e)
            raise
        except Exception as e:
            logger.error(f"❌ Channel info fetch failed: {e}")
            raise
    
    async def get_channel_videos_with_quota(self, channel_id: str, access_token: str, 
                                          user_id: Optional[str] = None, max_results: int = 50) -> List[Dict[str, Any]]:
        """Get channel videos with quota management"""
        # This operation requires multiple API calls
        self._check_and_record_quota("channels_list", user_id)  # For uploads playlist
        self._check_and_record_quota("playlist_items_list", user_id)  # For video list
        self._check_and_record_quota("videos_list", user_id)  # For video details
        
        try:
            credentials = Credentials(token=access_token)
            youtube = build('youtube', 'v3', credentials=credentials)
            
            # Get uploads playlist
            channels_request = youtube.channels().list(
                part='contentDetails',
                id=channel_id
            )
            channels_response = channels_request.execute()
            
            if not channels_response.get('items'):
                return []
            
            uploads_playlist_id = channels_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
            
            # Get playlist items
            playlist_request = youtube.playlistItems().list(
                part='snippet',
                playlistId=uploads_playlist_id,
                maxResults=min(max_results, 50)
            )
            playlist_response = playlist_request.execute()
            
            videos = []
            video_ids = []
            
            for item in playlist_response.get('items', []):
                video_id = item['snippet']['resourceId']['videoId']
                video_title = item['snippet']['title']
                
                # Skip unavailable videos
                if video_title in ['Deleted video', 'Private video', '[Deleted Video]', '[Private Video]']:
                    continue
                
                video_ids.append(video_id)
                videos.append({
                    "id": video_id,
                    "title": video_title,
                    "description": item['snippet']['description'],
                    "published_at": item['snippet']['publishedAt'],
                    "thumbnail_url": item['snippet']['thumbnails'].get('medium', {}).get('url', '')
                })
            
            # Get video statistics
            if video_ids:
                videos_request = youtube.videos().list(
                    part='statistics,contentDetails',
                    id=','.join(video_ids)
                )
                videos_response = videos_request.execute()
                
                for i, video_item in enumerate(videos_response.get('items', [])):
                    if i < len(videos):
                        statistics = video_item.get('statistics', {})
                        content_details = video_item.get('contentDetails', {})
                        
                        videos[i].update({
                            "view_count": int(statistics.get('viewCount', 0)),
                            "like_count": int(statistics.get('likeCount', 0)),
                            "comment_count": int(statistics.get('commentCount', 0)),
                            "duration": content_details.get('duration', 'PT0S')
                        })
            
            return videos
            
        except HttpError as e:
            self._handle_youtube_api_error(e)
            raise
        except Exception as e:
            logger.error(f"❌ Channel videos fetch failed: {e}")
            raise
    
    async def update_video_title_with_quota(self, video_id: str, new_title: str, access_token: str,
                                          user_id: Optional[str] = None) -> bool:
        """Update video title with quota management"""
        self._check_and_record_quota("videos_update", user_id)
        
        try:
            credentials = Credentials(token=access_token)
            youtube = build('youtube', 'v3', credentials=credentials)
            
            # First get current video details
            video_request = youtube.videos().list(
                part='snippet',
                id=video_id
            )
            video_response = video_request.execute()
            
            if not video_response.get('items'):
                logger.error(f"Video {video_id} not found")
                return False
            
            video = video_response['items'][0]
            snippet = video['snippet']
            
            # Update only the title
            snippet['title'] = new_title
            
            # Update the video
            update_request = youtube.videos().update(
                part='snippet',
                body={
                    'id': video_id,
                    'snippet': snippet
                }
            )
            update_response = update_request.execute()
            
            logger.info(f"✅ Updated video {video_id} title to: {new_title}")
            return True
            
        except HttpError as e:
            self._handle_youtube_api_error(e)
            return False
        except Exception as e:
            logger.error(f"❌ Video title update failed: {e}")
            return False
    
    def _handle_youtube_api_error(self, error: HttpError):
        """Handle YouTube API errors with proper classification"""
        error_content = error.content.decode('utf-8') if error.content else ""
        
        if error.resp.status == 403:
            if "quotaExceeded" in error_content:
                raise QuotaExceededException("YouTube API quota exceeded")
            elif "accessNotConfigured" in error_content:
                raise APIConfigurationError("YouTube API access not configured")
            else:
                raise PermissionError("YouTube API access denied")
        elif error.resp.status == 401:
            raise AuthenticationError("Invalid or expired YouTube API credentials")
        elif error.resp.status == 429:
            raise RateLimitExceededException("YouTube API rate limit exceeded")
        else:
            logger.error(f"❌ YouTube API error {error.resp.status}: {error_content}")
            raise

# Custom exceptions
class QuotaExceededException(Exception):
    """Raised when API quota is exceeded"""
    pass

class RateLimitExceededException(Exception):
    """Raised when API rate limit is exceeded"""
    pass

class APIConfigurationError(Exception):
    """Raised when API is not properly configured"""
    pass

class AuthenticationError(Exception):
    """Raised when API authentication fails"""
    pass

# Decorator for quota-aware API calls
def with_quota_management(operation: str):
    """Decorator to add quota management to API methods"""
    def decorator(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            user_id = kwargs.pop('user_id', None)
            
            try:
                # Check and record quota
                if hasattr(self, 'quota_manager'):
                    self.quota_manager.check_and_record_quota(operation, user_id)
                
                return await func(self, *args, **kwargs)
                
            except (QuotaExceededException, RateLimitExceededException):
                raise
            except Exception as e:
                logger.error(f"❌ API call failed: {e}")
                raise
        
        return wrapper
    return decorator

# Global quota manager instance
youtube_quota_manager = YouTubeQuotaManager()