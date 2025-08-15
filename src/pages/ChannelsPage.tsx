import { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { apiClient } from '@/lib/api-client';
import { toast } from 'sonner';
import { Plus, Youtube, Trash2 } from 'lucide-react';

export function ChannelsPage() {
  const [channels, setChannels] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadChannels();
  }, []);

  const loadChannels = async () => {
    try {
      setLoading(true);
      const data = await apiClient.getChannels();
      setChannels(data || []);
    } catch (error) {
      console.error('Failed to load channels:', error);
      toast.error('Failed to load channels');
    } finally {
      setLoading(false);
    }
  };

  const handleConnectChannel = () => {
    const base = import.meta.env.VITE_API_BASE_URL;
    if (!base) {
      throw new Error('[env] VITE_API_BASE_URL is missing. Set it to your v5 API, e.g. https://ttprov5.onrender.com');
    }
    window.location.href = `${base}/auth/oauth/initiate`;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">YouTube Channels</h1>
          <p className="text-muted-foreground mt-2">
            Connect and manage your YouTube channels
          </p>
        </div>
        <Button onClick={handleConnectChannel} className="gap-2">
          <Plus className="h-4 w-4" />
          Connect Channel
        </Button>
      </div>

      {channels.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <Youtube className="h-12 w-12 text-muted-foreground mb-4" />
            <h3 className="text-lg font-semibold mb-2">No channels connected</h3>
            <p className="text-muted-foreground text-center mb-4">
              Connect your YouTube channel to start creating A/B tests
            </p>
            <Button onClick={handleConnectChannel}>
              Connect Your First Channel
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {channels.map((channel) => (
            <Card key={channel.id}>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="h-10 w-10 rounded-full bg-muted flex items-center justify-center">
                      <Youtube className="h-5 w-5" />
                    </div>
                    <div>
                      <CardTitle className="text-base">{channel.title}</CardTitle>
                      <CardDescription className="text-xs">
                        {channel.channel_id}
                      </CardDescription>
                    </div>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-2 text-sm">
                  <div className="flex items-center justify-between">
                    <span className="text-muted-foreground">Subscribers</span>
                    <span>{channel.subscriber_count?.toLocaleString() || 'N/A'}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-muted-foreground">Videos</span>
                    <span>{channel.video_count?.toLocaleString() || 'N/A'}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-muted-foreground">Connected</span>
                    <span>{new Date(channel.created_at).toLocaleDateString()}</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}