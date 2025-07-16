import logging
from typing import List, Dict, Any, Optional
from .config import settings

logger = logging.getLogger(__name__)


class YouTubeAPIClient:
    """Mock YouTube API client for development"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or settings.youtube_api_key
        logger.info("Initialized mock YouTube API client")
    
    async def get_channel_info(self, access_token: str) -> Dict[str, Any]:
        """Get channel information for the authenticated user"""
        return {
            "id": "UC_mock_channel_id_123",
            "title": "Dev User's Channel",
            "description": "A mock YouTube channel for development",
            "subscriber_count": 1000,
            "video_count": 50,
            "view_count": 100000
        }
    
    async def get_channel_videos(self, channel_id: str, max_results: int = 50) -> List[Dict[str, Any]]:
        """Get videos from a channel"""
        mock_videos = []
        for i in range(min(max_results, 10)):
            mock_videos.append({
                "id": f"mock_video_id_{i}",
                "title": f"Sample Video Title {i + 1}",
                "description": f"This is a sample video description for video {i + 1}",
                "published_at": "2024-01-01T00:00:00Z",
                "view_count": 1000 + (i * 100),
                "like_count": 50 + (i * 5),
                "comment_count": 10 + i,
                "duration": "PT5M30S",
                "thumbnail_url": f"https://via.placeholder.com/320x180?text=Video+{i+1}"
            })
        return mock_videos
    
    async def get_video_details(self, video_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific video"""
        return {
            "id": video_id,
            "title": f"Sample Video Title for {video_id}",
            "description": "This is a sample video description",
            "published_at": "2024-01-01T00:00:00Z",
            "view_count": 5000,
            "like_count": 250,
            "comment_count": 50,
            "duration": "PT10M15S",
            "thumbnail_url": f"https://via.placeholder.com/320x180?text={video_id}",
            "tags": ["sample", "video", "test"],
            "category_id": "22"
        }
    
    async def update_video_title(self, video_id: str, new_title: str, access_token: str) -> bool:
        """Update a video's title"""
        logger.info(f"Mock: Updating video {video_id} title to: {new_title}")
        return True
    
    async def get_video_analytics(self, video_id: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """Get analytics data for a video (mock implementation)"""
        return {
            "video_id": video_id,
            "views": 1000,
            "impressions": 5000,
            "click_through_rate": 0.2,
            "average_view_duration": 300,
            "likes": 50,
            "dislikes": 2,
            "comments": 25,
            "shares": 10,
            "subscribers_gained": 5
        }


youtube_client = YouTubeAPIClient()


def get_youtube_client() -> YouTubeAPIClient:
    """Dependency injection for YouTube API client"""
    return youtube_client
