'use client'

import { useState, useEffect } from 'react';
import useSWR from 'swr';
import { getYouTubeChannels, getYouTubeVideos } from '@/lib/api';
import { Button } from '@/components/ui/button';
import Card from '@/components/ui/Card';

interface Channel {
  id: string;
  title: string;
  thumbnail?: string;
}

interface Video {
  id: string;
  title: string;
  thumbnail?: string;
}

interface YouTubePickerProps {
  onSelectionChange: (selection: { channelId: string; videoIds: string[] }) => void;
}

export default function YouTubePicker({ onSelectionChange }: YouTubePickerProps) {
  const [selectedChannelId, setSelectedChannelId] = useState<string>('');
  const [selectedVideoIds, setSelectedVideoIds] = useState<string[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [currentPage, setCurrentPage] = useState('');

  const { data: channels, error: channelsError } = useSWR('youtube-channels', getYouTubeChannels);
  const { data: videosData, error: videosError } = useSWR(
    selectedChannelId ? ['youtube-videos', searchQuery, currentPage] : null,
    () => getYouTubeVideos({ q: searchQuery, page: currentPage })
  );

  const videos = videosData?.items || [];
  const nextPageToken = videosData?.nextPageToken;

  useEffect(() => {
    onSelectionChange({ channelId: selectedChannelId, videoIds: selectedVideoIds });
  }, [selectedChannelId, selectedVideoIds, onSelectionChange]);

  const handleChannelSelect = (channelId: string) => {
    setSelectedChannelId(channelId);
    setSelectedVideoIds([]);
    setCurrentPage('');
  };

  const handleVideoToggle = (videoId: string) => {
    setSelectedVideoIds(prev => 
      prev.includes(videoId)
        ? prev.filter(id => id !== videoId)
        : [...prev, videoId]
    );
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setCurrentPage('');
  };

  const handleLoadMore = () => {
    setCurrentPage(nextPageToken);
  };

  if (channelsError) {
    return (
      <Card>
        <div className="text-center py-8">
          <p className="text-red-600">Failed to load YouTube channels. Please try again.</p>
        </div>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Channel Selection */}
      <Card>
        <h3 className="text-lg font-semibold text-slate-900 mb-4">Select YouTube Channel</h3>
        {!channels ? (
          <div className="animate-pulse space-y-3">
            {[1, 2, 3].map(i => (
              <div key={i} className="flex items-center space-x-3">
                <div className="w-12 h-12 bg-slate-200 rounded-full" />
                <div className="flex-1 h-4 bg-slate-200 rounded" />
              </div>
            ))}
          </div>
        ) : (
          <div className="space-y-3">
            {channels.map((channel: Channel) => (
              <div 
                key={channel.id}
                className={`flex items-center space-x-3 p-3 rounded-xl cursor-pointer transition-colors ${
                  selectedChannelId === channel.id
                    ? 'bg-blue-50 border border-blue-200'
                    : 'hover:bg-slate-50'
                }`}
                onClick={() => handleChannelSelect(channel.id)}
              >
                <input
                  type="radio"
                  checked={selectedChannelId === channel.id}
                  onChange={() => handleChannelSelect(channel.id)}
                  className="text-blue-600"
                />
                {channel.thumbnail && (
                  <img 
                    src={channel.thumbnail} 
                    alt={channel.title}
                    className="w-12 h-12 rounded-full object-cover"
                  />
                )}
                <span className="font-medium text-slate-900">{channel.title}</span>
              </div>
            ))}
          </div>
        )}
      </Card>

      {/* Video Selection */}
      {selectedChannelId && (
        <Card>
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-slate-900">Select Videos</h3>
            <span className="text-sm text-slate-500">
              {selectedVideoIds.length} selected
            </span>
          </div>

          {/* Search */}
          <form onSubmit={handleSearch} className="mb-4">
            <div className="flex gap-2">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search videos..."
                className="flex-1 px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <Button type="submit" variant="outline">
                Search
              </Button>
            </div>
          </form>

          {/* Videos List */}
          {videosError ? (
            <div className="text-center py-8">
              <p className="text-red-600">Failed to load videos. Please try again.</p>
            </div>
          ) : !videos.length ? (
            <div className="animate-pulse space-y-3">
              {[1, 2, 3].map(i => (
                <div key={i} className="flex items-center space-x-3">
                  <div className="w-4 h-4 bg-slate-200 rounded" />
                  <div className="w-24 h-16 bg-slate-200 rounded" />
                  <div className="flex-1 h-4 bg-slate-200 rounded" />
                </div>
              ))}
            </div>
          ) : (
            <div className="space-y-3">
              {videos.map((video: Video) => (
                <div 
                  key={video.id}
                  className={`flex items-center space-x-3 p-3 rounded-xl cursor-pointer transition-colors ${
                    selectedVideoIds.includes(video.id)
                      ? 'bg-blue-50 border border-blue-200'
                      : 'hover:bg-slate-50'
                  }`}
                  onClick={() => handleVideoToggle(video.id)}
                >
                  <input
                    type="checkbox"
                    checked={selectedVideoIds.includes(video.id)}
                    onChange={() => handleVideoToggle(video.id)}
                    className="text-blue-600"
                  />
                  {video.thumbnail && (
                    <img 
                      src={video.thumbnail} 
                      alt={video.title}
                      className="w-24 h-16 rounded object-cover"
                    />
                  )}
                  <span className="flex-1 text-sm font-medium text-slate-900 line-clamp-2">
                    {video.title}
                  </span>
                </div>
              ))}
              
              {nextPageToken && (
                <div className="text-center pt-4">
                  <Button variant="outline" onClick={handleLoadMore}>
                    Load More Videos
                  </Button>
                </div>
              )}
            </div>
          )}
        </Card>
      )}
    </div>
  );
}