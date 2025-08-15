import { useState, useEffect } from 'react';
import { apiClient } from '../lib/api-client';

interface Video {
  id: string;
  title: string;
  description: string;
  published_at: string;
  thumbnail_url: string;
  view_count: number;
  duration: string;
}

interface VideoSelectorProps {
  selectedVideoId: string;
  onVideoSelect: (videoId: string, videoTitle: string) => void;
  className?: string;
}

export function VideoSelector({ selectedVideoId, onVideoSelect, className = '' }: VideoSelectorProps) {
  const [videos, setVideos] = useState<Video[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [isOpen, setIsOpen] = useState(false);

  const selectedVideo = videos.find(video => video.id === selectedVideoId);

  useEffect(() => {
    fetchChannelVideos();
  }, []);

  const fetchChannelVideos = async () => {
    setLoading(true);
    setError('');
    
    try {
      const data = await apiClient.getChannelVideos(50);
      setVideos(data.videos || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch videos');
    } finally {
      setLoading(false);
    }
  };

  const formatDuration = (duration: string) => {
    const match = duration.match(/PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?/);
    if (!match) return duration;
    
    const hours = parseInt(match[1] || '0');
    const minutes = parseInt(match[2] || '0');
    const seconds = parseInt(match[3] || '0');
    
    if (hours > 0) {
      return `${hours}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    }
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  };

  const formatViewCount = (count: number) => {
    if (count >= 1000000) {
      return `${(count / 1000000).toFixed(1)}M views`;
    } else if (count >= 1000) {
      return `${(count / 1000).toFixed(1)}K views`;
    }
    return `${count} views`;
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  if (loading) {
    return (
      <div className={`${className}`}>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Select Video
        </label>
        <div className="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50">
          Loading videos...
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`${className}`}>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Select Video
        </label>
        <div className="w-full px-3 py-2 border border-red-300 rounded-md bg-red-50 text-red-600">
          {error}
        </div>
        <button
          type="button"
          onClick={fetchChannelVideos}
          className="mt-2 text-sm text-blue-600 hover:text-blue-800"
        >
          Try again
        </button>
      </div>
    );
  }

  return (
    <div className={`relative ${className}`}>
      <label className="block text-sm font-medium text-gray-700 mb-1">
        Select Video
      </label>
      
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white text-left flex items-center justify-between"
      >
        {selectedVideo ? (
          <div className="flex items-center space-x-3">
            <img
              src={selectedVideo.thumbnail_url}
              alt={selectedVideo.title}
              className="w-12 h-9 object-cover rounded"
            />
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-900 truncate">
                {selectedVideo.title}
              </p>
              <p className="text-xs text-gray-500">
                {formatViewCount(selectedVideo.view_count)} • {formatDate(selectedVideo.published_at)}
              </p>
            </div>
          </div>
        ) : (
          <span className="text-gray-500">Choose a video from your channel</span>
        )}
        <svg
          className={`w-5 h-5 text-gray-400 transition-transform ${isOpen ? 'rotate-180' : ''}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {isOpen && (
        <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-md shadow-lg max-h-60 overflow-y-auto">
          {videos.length === 0 ? (
            <div className="px-3 py-2 text-sm text-gray-500">
              No videos found in your channel
            </div>
          ) : (
            videos.map((video) => (
              <button
                key={video.id}
                type="button"
                onClick={() => {
                  onVideoSelect(video.id, video.title);
                  setIsOpen(false);
                }}
                className="w-full px-3 py-2 text-left hover:bg-gray-50 focus:bg-gray-50 focus:outline-none border-b border-gray-100 last:border-b-0"
              >
                <div className="flex items-center space-x-3">
                  <img
                    src={video.thumbnail_url}
                    alt={video.title}
                    className="w-16 h-12 object-cover rounded"
                  />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">
                      {video.title}
                    </p>
                    <div className="flex items-center space-x-2 text-xs text-gray-500">
                      <span>{formatViewCount(video.view_count)}</span>
                      <span>•</span>
                      <span>{formatDuration(video.duration)}</span>
                      <span>•</span>
                      <span>{formatDate(video.published_at)}</span>
                    </div>
                  </div>
                </div>
              </button>
            ))
          )}
        </div>
      )}
    </div>
  );
}
