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
        
        logger.debug(f"get_channel_info called with access_token length: {len(access_token) if access_token else 0}")
        
        
        try:
            logger.debug("Creating YouTube API credentials and client")
            credentials = Credentials(token=access_token)
            youtube = build('youtube', 'v3', credentials=credentials)
            
            logger.debug("Making YouTube API call to channels().list()")
            request = youtube.channels().list(
                part='snippet,statistics',
                mine=True
            )
            response = request.execute()
            
            logger.debug(f"YouTube API response received with {len(response.get('items', []))} channels")
            
            if not response.get('items'):
                logger.error("No YouTube channel found for the authenticated user")
                raise ValueError("No channel found for the authenticated user")
            
            channel = response['items'][0]
            snippet = channel.get('snippet', {})
            statistics = channel.get('statistics', {})
            
            channel_info = {
                "id": channel['id'],
                "title": snippet.get('title', ''),
                "description": snippet.get('description', ''),
                "subscriber_count": int(statistics.get('subscriberCount', 0)),
                "video_count": int(statistics.get('videoCount', 0)),
                "view_count": int(statistics.get('viewCount', 0))
            }
            
            logger.info(f"Successfully fetched channel info: {channel_info['title']} (ID: {channel_info['id']})")
            return channel_info
            
        except Exception as e:
            logger.error(f"Error fetching channel info: {e}", exc_info=True)
            
            error_str = str(e).lower()
            if "invalid_token" in error_str or "unauthorized" in error_str:
                raise ValueError("Invalid or expired access token")
            elif "forbidden" in error_str or "access_denied" in error_str:
                raise ValueError("Access denied - insufficient permissions for YouTube API")
            elif "quota" in error_str:
                raise ValueError("YouTube API quota exceeded")
            else:
                raise
    
    async def get_channel_videos(self, channel_id: str, access_token: str, max_results: int = 50) -> List[Dict[str, Any]]:
        """Get videos from a channel"""
        from .config import settings
        
        logger.debug(f"get_channel_videos called with channel_id: {channel_id}, max_results: {max_results}")
        
        
        try:
            logger.debug("Creating YouTube API credentials and client for video fetching")
            credentials = Credentials(token=access_token)
            youtube = build('youtube', 'v3', credentials=credentials)
            
            logger.debug(f"Fetching channel content details for channel: {channel_id}")
            channels_request = youtube.channels().list(
                part='contentDetails',
                id=channel_id
            )
            channels_response = channels_request.execute()
            
            if not channels_response.get('items'):
                logger.warning(f"No channel found with ID: {channel_id}")
                return []
            
            uploads_playlist_id = channels_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
            logger.debug(f"Found uploads playlist ID: {uploads_playlist_id}")
            
            # Fetch more items initially to account for deleted/private videos
            fetch_limit = min(max_results * 2, 50)  # Fetch double to account for filtered videos
            logger.debug(f"Fetching playlist items with max_results: {fetch_limit}")
            playlist_request = youtube.playlistItems().list(
                part='snippet',
                playlistId=uploads_playlist_id,
                maxResults=fetch_limit
            )
            playlist_response = playlist_request.execute()
            
            videos = []
            video_ids = []
            
            for item in playlist_response.get('items', []):
                video_id = item['snippet']['resourceId']['videoId']
                video_title = item['snippet']['title']
                
                # Skip deleted, private, or unavailable videos
                if video_title in ['Deleted video', 'Private video', '[Deleted Video]', '[Private Video]']:
                    logger.debug(f"Skipping unavailable video: {video_id} - {video_title}")
                    continue
                
                video_ids.append(video_id)
                
                videos.append({
                    "id": video_id,
                    "title": video_title,
                    "description": item['snippet']['description'],
                    "published_at": item['snippet']['publishedAt'],
                    "thumbnail_url": item['snippet']['thumbnails'].get('medium', {}).get('url', '')
                })
            
            logger.debug(f"Found {len(video_ids)} videos, fetching detailed statistics")
            
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
            
            # If we don't have enough videos and there's a next page, fetch more
            if len(videos) < max_results and playlist_response.get('nextPageToken'):
                logger.debug(f"Only got {len(videos)} videos, fetching next page...")
                try:
                    next_request = youtube.playlistItems().list(
                        part='snippet',
                        playlistId=uploads_playlist_id,
                        maxResults=min(max_results - len(videos), 50),
                        pageToken=playlist_response['nextPageToken']
                    )
                    next_response = next_request.execute()
                    
                    additional_videos = []
                    additional_video_ids = []
                    
                    for item in next_response.get('items', []):
                        video_id = item['snippet']['resourceId']['videoId']
                        video_title = item['snippet']['title']
                        
                        # Skip deleted, private, or unavailable videos
                        if video_title in ['Deleted video', 'Private video', '[Deleted Video]', '[Private Video]']:
                            logger.debug(f"Skipping unavailable video: {video_id} - {video_title}")
                            continue
                            
                        if len(videos) + len(additional_videos) >= max_results:
                            break
                        
                        additional_video_ids.append(video_id)
                        additional_videos.append({
                            "id": video_id,
                            "title": video_title,
                            "description": item['snippet']['description'],
                            "published_at": item['snippet']['publishedAt'],
                            "thumbnail_url": item['snippet']['thumbnails'].get('medium', {}).get('url', '')
                        })
                    
                    # Get statistics for additional videos
                    if additional_video_ids:
                        additional_videos_request = youtube.videos().list(
                            part='statistics,contentDetails',
                            id=','.join(additional_video_ids)
                        )
                        additional_videos_response = additional_videos_request.execute()
                        
                        for i, video_item in enumerate(additional_videos_response.get('items', [])):
                            if i < len(additional_videos):
                                statistics = video_item.get('statistics', {})
                                content_details = video_item.get('contentDetails', {})
                                
                                additional_videos[i].update({
                                    "view_count": int(statistics.get('viewCount', 0)),
                                    "like_count": int(statistics.get('likeCount', 0)),
                                    "comment_count": int(statistics.get('commentCount', 0)),
                                    "duration": content_details.get('duration', 'PT0S')
                                })
                    
                    videos.extend(additional_videos)
                    logger.debug(f"Added {len(additional_videos)} more videos from next page")
                    
                except Exception as e:
                    logger.warning(f"Failed to fetch additional videos: {e}")
            
            logger.info(f"Successfully fetched {len(videos)} videos for channel {channel_id}")
            return videos[:max_results]  # Ensure we don't exceed requested limit
            
        except Exception as e:
            logger.error(f"Error fetching channel videos for channel {channel_id}: {e}", exc_info=True)
            
            error_str = str(e).lower()
            if "invalid_token" in error_str or "unauthorized" in error_str:
                raise ValueError("Invalid or expired access token")
            elif "forbidden" in error_str or "access_denied" in error_str:
                raise ValueError("Access denied - insufficient permissions for YouTube API")
            elif "quota" in error_str:
                raise ValueError("YouTube API quota exceeded")
            elif "not found" in error_str:
                raise ValueError(f"Channel not found: {channel_id}")
            else:
                raise
    
    async def get_video_details(self, video_id: str, access_token: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific video"""
        from .config import settings
        
        logger.info(f"get_video_details called with video_id: {video_id}")
        
        try:
            credentials = Credentials(token=access_token)
            youtube = build('youtube', 'v3', credentials=credentials)
            
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
