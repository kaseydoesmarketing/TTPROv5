import { useState, useEffect } from 'react';

interface Channel {
  id: string;
  channel_id: string;
  channel_title: string;
  channel_description: string;
  subscriber_count: number;
  video_count: number;
  view_count: number;
  thumbnail_url: string;
  custom_url: string;
  is_active: boolean;
  is_selected: boolean;
  created_at: string;
  updated_at: string;
}

export function ChannelSelector() {
  const [channels, setChannels] = useState<Channel[]>([]);
  const [selectedChannel, setSelectedChannel] = useState<Channel | null>(null);
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const API_BASE = import.meta.env.VITE_API_BASE_URL;

  const fetchJSON = async (path: string, init?: RequestInit) => {
    if (!API_BASE) throw new Error('[env] VITE_API_BASE_URL missing');
    const res = await fetch(`${API_BASE}${path}`, { credentials: 'include', ...(init || {}) });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
  };

  const fetchChannels = async () => {
    try {
      const channelsData = await fetchJSON('/api/channels/');
      setChannels(channelsData);
      const selected = channelsData.find((ch: Channel) => ch.is_selected);
      setSelectedChannel(selected || channelsData[0] || null);
    } catch (error) {
      console.error('Error fetching channels:', error);
      setError('Failed to load channels');
    }
  };

  const syncChannels = async () => {
    try {
      setLoading(true);
      setError(null);
      const channelsData = await fetchJSON('/api/channels/sync', { method: 'POST' });
      setChannels(channelsData);
      const selected = channelsData.find((ch: Channel) => ch.is_selected);
      setSelectedChannel(selected || channelsData[0] || null);
    } catch (error) {
      console.error('Error syncing channels:', error);
      setError('Failed to sync channels');
    } finally {
      setLoading(false);
    }
  };

  const selectChannel = async (channelId: string) => {
    try {
      setLoading(true);
      setError(null);
      const result = await fetchJSON(`/api/channels/${channelId}/select`, { method: 'POST' });
      setSelectedChannel(result.channel);
      setChannels(prev => prev.map(ch => ({ ...ch, is_selected: ch.channel_id === channelId })));
      setIsOpen(false);
    } catch (error) {
      console.error('Error selecting channel:', error);
      setError('Failed to select channel');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchChannels(); }, []);
  useEffect(() => { if (channels.length === 0) syncChannels(); }, [channels.length]);

  if (channels.length === 0 && !loading) {
    return (
      <div className="flex items-center space-x-2">
        <button onClick={syncChannels} disabled={loading} className="text-sm text-blue-600 hover:text-blue-700 disabled:opacity-50">
          {loading ? 'Syncing...' : 'Sync Channels'}
        </button>
      </div>
    );
  }

  if (channels.length <= 1) {
    return selectedChannel ? (
      <div className="flex items-center space-x-2">
        {selectedChannel.thumbnail_url && (
          <img src={selectedChannel.thumbnail_url} alt={selectedChannel.channel_title} className="w-6 h-6 rounded-full" />
        )}
        <span className="text-sm text-gray-700 max-w-32 truncate">{selectedChannel.channel_title}</span>
      </div>
    ) : null;
  }

  return (
    <div className="relative">
      <button onClick={() => setIsOpen(!isOpen)} disabled={loading} className="flex items-center space-x-2 text-sm text-gray-700 hover:text-gray-900 disabled:opacity-50">
        {selectedChannel?.thumbnail_url && (
          <img src={selectedChannel.thumbnail_url} alt={selectedChannel.channel_title} className="w-6 h-6 rounded-full" />
        )}
        <span className="max-w-32 truncate">{selectedChannel?.channel_title || 'Select Channel'}</span>
        <svg className={`w-4 h-4 transition-transform ${isOpen ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-64 bg-white rounded-md shadow-lg ring-1 ring-black ring-opacity-5 z-50">
          <div className="py-1">
            <div className="px-4 py-2 text-xs font-medium text-gray-500 uppercase tracking-wide border-b">YouTube Channels</div>
            {channels.map((channel) => (
              <button key={channel.id} onClick={() => selectChannel(channel.channel_id)} disabled={loading} className={`w-full text-left px-4 py-3 text-sm hover:bg-gray-50 disabled:opacity-50 flex items-center space-x-3 ${channel.is_selected ? 'bg-blue-50 text-blue-700' : 'text-gray-700'}`}>
                {channel.thumbnail_url && (<img src={channel.thumbnail_url} alt={channel.channel_title} className="w-8 h-8 rounded-full flex-shrink-0" />)}
                <div className="flex-1 min-w-0">
                  <div className="font-medium truncate">{channel.channel_title}</div>
                  <div className="text-xs text-gray-500">{channel.subscriber_count.toLocaleString()} subscribers • {channel.video_count} videos</div>
                </div>
                {channel.is_selected && (<svg className="w-4 h-4 text-blue-600" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" /></svg>)}
              </button>
            ))}
            <div className="border-t">
              <button onClick={syncChannels} disabled={loading} className="w-full text-left px-4 py-2 text-sm text-blue-600 hover:bg-gray-50 disabled:opacity-50">{loading ? 'Syncing...' : 'Refresh Channels'}</button>
            </div>
          </div>
        </div>
      )}

      {error && (<div className="absolute right-0 mt-1 text-xs text-red-600">{error}</div>)}
    </div>
  );
}
