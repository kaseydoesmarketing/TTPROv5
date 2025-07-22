import logging
from typing import List, Dict, Any, Optional
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from .config import settings

logger = logging.getLogger(__name__)


class YouTubeAPIClient:
    """Real YouTube API client using Google YouTube Data API v3"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.youtube_api_key
        logger.info("Initialized YouTube API client")
    
    async def get_channel_info(self, access_token: str) -> Dict[str, Any]:
        """Get channel information for the authenticated user"""
        from .config import settings
        
        if settings.is_development and access_token == "dev_access_token":
            logger.info("Using development bypass for channel info")
            return {
                "id": "dev_channel_123",
                "title": "Development Channel",
                "description": "A development channel for testing TitleTesterPro",
                "subscriber_count": 1000,
                "video_count": 25,
                "view_count": 50000,
                "thumbnail_url": "https://via.placeholder.com/88x88"
            }
        
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
        except Exception as e:
            logger.error(f"Error fetching channel info: {e}")
            raise
    
    async def get_channel_videos(self, channel_id: str, max_results: int = 50) -> List[Dict[str, Any]]:
        """Get videos from a channel"""
        from .config import settings
        
        if settings.is_development and channel_id == "dev_channel_123":
            logger.info("Using development bypass for channel videos")
            return [
                {
                    "id": "dev_video_1",
                    "title": "How to Optimize YouTube Titles for Maximum Views",
                    "description": "Learn the secrets of creating compelling YouTube titles that drive engagement and views.",
                    "published_at": "2024-01-15T10:00:00Z",
                    "thumbnail_url": "https://via.placeholder.com/320x180",
                    "view_count": 15420,
                    "like_count": 892,
                    "comment_count": 156,
                    "duration": "PT8M32S"
                },
                {
                    "id": "dev_video_2", 
                    "title": "A/B Testing Your YouTube Content: Complete Guide",
                    "description": "Master the art of A/B testing to improve your YouTube performance and grow your channel.",
                    "published_at": "2024-01-10T14:30:00Z",
                    "thumbnail_url": "https://via.placeholder.com/320x180",
                    "view_count": 8765,
                    "like_count": 543,
                    "comment_count": 89,
                    "duration": "PT12M15S"
                },
                {
                    "id": "dev_video_3",
                    "title": "YouTube Analytics Deep Dive: Understanding Your Metrics",
                    "description": "Comprehensive guide to YouTube analytics and how to use data to grow your channel.",
                    "published_at": "2024-01-05T09:15:00Z",
                    "thumbnail_url": "https://via.placeholder.com/320x180",
                    "view_count": 12340,
                    "like_count": 678,
                    "comment_count": 234,
                    "duration": "PT15M42S"
                }
            ]
        
        try:
            youtube = build('youtube', 'v3', developerKey=self.api_key)
            
            channels_request = youtube.channels().list(
                part='contentDetails',
                id=channel_id
            )
            channels_response = channels_request.execute()
            
            if not channels_response.get('items'):
                return []
            
            uploads_playlist_id = channels_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
            
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
                video_ids.append(video_id)
                
                videos.append({
                    "id": video_id,
                    "title": item['snippet']['title'],
                    "description": item['snippet']['description'],
                    "published_at": item['snippet']['publishedAt'],
                    "thumbnail_url": item['snippet']['thumbnails'].get('medium', {}).get('url', '')
                })
            
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
        except Exception as e:
            logger.error(f"Error fetching channel videos: {e}")
            raise
    
    async def get_video_details(self, video_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific video"""
        try:
            youtube = build('youtube', 'v3', developerKey=self.api_key)
            
            request = youtube.videos().list(
                part='snippet,statistics,contentDetails',
                id=video_id
            )
            response = request.execute()
            
            if not response.get('items'):
                return None
            
            video = response['items'][0]
            snippet = video.get('snippet', {})
            statistics = video.get('statistics', {})
            content_details = video.get('contentDetails', {})
            
            return {
                "id": video_id,
                "title": snippet.get('title', ''),
                "description": snippet.get('description', ''),
                "published_at": snippet.get('publishedAt', ''),
                "view_count": int(statistics.get('viewCount', 0)),
                "like_count": int(statistics.get('likeCount', 0)),
                "comment_count": int(statistics.get('commentCount', 0)),
                "duration": content_details.get('duration', 'PT0S'),
                "thumbnail_url": snippet.get('thumbnails', {}).get('medium', {}).get('url', ''),
                "tags": snippet.get('tags', []),
                "category_id": snippet.get('categoryId', '')
            }
        except Exception as e:
            logger.error(f"Error fetching video details: {e}")
            return None
    
    async def update_video_title(self, video_id: str, new_title: str, access_token: str) -> bool:
        """Update a video's title"""
        try:
            credentials = Credentials(token=access_token)
            youtube = build('youtube', 'v3', credentials=credentials)
            
            get_request = youtube.videos().list(
                part='snippet',
                id=video_id
            )
            get_response = get_request.execute()
            
            if not get_response.get('items'):
                logger.error(f"Video {video_id} not found")
                return False
            
            video = get_response['items'][0]
            snippet = video['snippet']
            
            snippet['title'] = new_title
            
            update_request = youtube.videos().update(
                part='snippet',
                body={
                    'id': video_id,
                    'snippet': snippet
                }
            )
            update_response = update_request.execute()
            
            logger.info(f"Successfully updated video {video_id} title to: {new_title}")
            return True
        except Exception as e:
            logger.error(f"Error updating video title: {e}")
            return False
    
    async def get_video_analytics(self, video_id: str, start_date: str, end_date: str, access_token: str) -> Dict[str, Any]:
        """Get analytics data for a video using YouTube Analytics API"""
        try:
            credentials = Credentials(token=access_token)
            youtube_analytics = build('youtubeAnalytics', 'v2', credentials=credentials)
            
            request = youtube_analytics.reports().query(
                ids='channel==MINE',
                startDate=start_date,
                endDate=end_date,
                metrics='views,likes,comments,shares,subscribersGained,averageViewDuration,impressions,estimatedMinutesWatched',
                dimensions='video',
                filters=f'video=={video_id}',
                sort='day'
            )
            response = request.execute()
            
            if not response.get('rows'):
                logger.warning(f"No analytics data found for video {video_id}")
                return {
                    "video_id": video_id,
                    "views": 0,
                    "impressions": 0,
                    "click_through_rate": 0.0,
                    "average_view_duration": 0,
                    "likes": 0,
                    "comments": 0,
                    "shares": 0,
                    "subscribers_gained": 0,
                    "estimated_minutes_watched": 0
                }
            
            row = response['rows'][0]
            views = row[1] if len(row) > 1 else 0
            likes = row[2] if len(row) > 2 else 0
            comments = row[3] if len(row) > 3 else 0
            shares = row[4] if len(row) > 4 else 0
            subscribers_gained = row[5] if len(row) > 5 else 0
            average_view_duration = row[6] if len(row) > 6 else 0
            impressions = row[7] if len(row) > 7 else 0
            estimated_minutes_watched = row[8] if len(row) > 8 else 0
            
            click_through_rate = (views / impressions) if impressions > 0 else 0.0
            
            return {
                "video_id": video_id,
                "views": int(views),
                "impressions": int(impressions),
                "click_through_rate": round(click_through_rate, 4),
                "average_view_duration": int(average_view_duration),
                "likes": int(likes),
                "comments": int(comments),
                "shares": int(shares),
                "subscribers_gained": int(subscribers_gained),
                "estimated_minutes_watched": int(estimated_minutes_watched)
            }
        except Exception as e:
            logger.error(f"Error fetching video analytics: {e}")
            return {
                "video_id": video_id,
                "views": 0,
                "impressions": 0,
                "click_through_rate": 0.0,
                "average_view_duration": 0,
                "likes": 0,
                "comments": 0,
                "shares": 0,
                "subscribers_gained": 0,
                "estimated_minutes_watched": 0
            }


youtube_client = YouTubeAPIClient()


def get_youtube_client() -> YouTubeAPIClient:
    """Dependency injection for YouTube API client"""
    return youtube_client
