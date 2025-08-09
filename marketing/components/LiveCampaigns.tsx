'use client'

import { useState } from 'react';
import useSWR, { mutate } from 'swr';
import { differenceInSeconds, format } from 'date-fns';
import { Button } from '@/components/ui/button';
import Card from '@/components/ui/Card';
import Badge from '@/components/ui/Badge';
import Progress from '@/components/ui/Progress';
import { getCampaigns, pauseCampaign, resumeCampaign, stopCampaign } from '@/lib/api';

interface Campaign {
  id: string;
  status: 'running' | 'paused' | 'stopped' | 'completed';
  titles: string[];
  videoIds: string[];
  channelId: string;
  intervalMinutes: number;
  durationHours: number;
  nextRotationAt?: string;
  startedAt: string;
  endsAt: string;
  thumbnails?: string[];
}

export default function LiveCampaigns() {
  const [actionLoading, setActionLoading] = useState<{ [key: string]: string }>({});
  
  const { data: campaigns, error, isLoading } = useSWR('campaigns', getCampaigns, {
    refreshInterval: 15000, // Refresh every 15 seconds
  });

  const handleAction = async (campaignId: string, action: 'pause' | 'resume' | 'stop') => {
    setActionLoading(prev => ({ ...prev, [campaignId]: action }));
    
    try {
      switch (action) {
        case 'pause':
          await pauseCampaign(campaignId);
          break;
        case 'resume':
          await resumeCampaign(campaignId);
          break;
        case 'stop':
          await stopCampaign(campaignId);
          break;
      }
      
      // Optimistically update and then revalidate
      await mutate('campaigns');
    } catch (error) {
      console.error(`Failed to ${action} campaign:`, error);
    } finally {
      setActionLoading(prev => {
        const newState = { ...prev };
        delete newState[campaignId];
        return newState;
      });
    }
  };

  const getCountdown = (nextRotationAt: string) => {
    const seconds = differenceInSeconds(new Date(nextRotationAt), new Date());
    if (seconds <= 0) return 'Rotating now...';
    
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    
    if (minutes > 0) {
      return `${minutes}m ${remainingSeconds}s`;
    }
    return `${remainingSeconds}s`;
  };

  const getProgress = (campaign: Campaign) => {
    const now = new Date();
    const start = new Date(campaign.startedAt);
    const end = new Date(campaign.endsAt);
    
    const total = end.getTime() - start.getTime();
    const elapsed = now.getTime() - start.getTime();
    
    return Math.min(Math.max((elapsed / total) * 100, 0), 100);
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'running':
        return <Badge variant="success">Running</Badge>;
      case 'paused':
        return <Badge variant="warning">Paused</Badge>;
      case 'stopped':
        return <Badge variant="error">Stopped</Badge>;
      case 'completed':
        return <Badge variant="info">Completed</Badge>;
      default:
        return <Badge>{status}</Badge>;
    }
  };

  if (error) {
    return (
      <Card>
        <div className="text-center py-8">
          <p className="text-red-600">Failed to load campaigns. Please try again.</p>
          <Button 
            variant="outline" 
            onClick={() => mutate('campaigns')}
            className="mt-4"
          >
            Retry
          </Button>
        </div>
      </Card>
    );
  }

  if (isLoading) {
    return (
      <Card>
        <div className="space-y-4">
          <h2 className="text-lg font-semibold text-slate-900">Live Campaigns</h2>
          <div className="space-y-4">
            {[1, 2, 3].map(i => (
              <div key={i} className="animate-pulse">
                <div className="flex items-center space-x-4 p-4 border border-slate-200 rounded-xl">
                  <div className="flex space-x-2">
                    {[1, 2, 3].map(j => (
                      <div key={j} className="w-16 h-12 bg-slate-200 rounded" />
                    ))}
                  </div>
                  <div className="flex-1 space-y-2">
                    <div className="h-4 bg-slate-200 rounded w-3/4" />
                    <div className="h-3 bg-slate-200 rounded w-1/2" />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </Card>
    );
  }

  if (!campaigns || campaigns.length === 0) {
    return (
      <Card>
        <div className="text-center py-8">
          <div className="w-16 h-16 bg-slate-100 rounded-full mx-auto mb-4 flex items-center justify-center">
            <svg className="w-8 h-8 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
            </svg>
          </div>
          <h3 className="text-lg font-medium text-slate-900 mb-2">No Active Campaigns</h3>
          <p className="text-slate-600">Create your first A/B test campaign to get started.</p>
        </div>
      </Card>
    );
  }

  return (
    <Card>
      <div className="space-y-6">
        <h2 className="text-lg font-semibold text-slate-900">Live Campaigns</h2>
        
        <div className="space-y-4">
          {campaigns.map((campaign: Campaign) => (
            <div key={campaign.id} className="border border-slate-200 rounded-xl p-6">
              {/* Header */}
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-3">
                  {getStatusBadge(campaign.status)}
                  <span className="text-sm text-slate-500">
                    {campaign.videoIds.length} video{campaign.videoIds.length !== 1 ? 's' : ''}
                  </span>
                </div>
                
                <div className="flex items-center space-x-2">
                  {campaign.status === 'running' && (
                    <>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleAction(campaign.id, 'pause')}
                        disabled={actionLoading[campaign.id] === 'pause'}
                      >
                        {actionLoading[campaign.id] === 'pause' ? 'Pausing...' : 'Pause'}
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleAction(campaign.id, 'stop')}
                        disabled={actionLoading[campaign.id] === 'stop'}
                      >
                        {actionLoading[campaign.id] === 'stop' ? 'Stopping...' : 'Stop'}
                      </Button>
                    </>
                  )}
                  
                  {campaign.status === 'paused' && (
                    <>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleAction(campaign.id, 'resume')}
                        disabled={actionLoading[campaign.id] === 'resume'}
                      >
                        {actionLoading[campaign.id] === 'resume' ? 'Resuming...' : 'Resume'}
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleAction(campaign.id, 'stop')}
                        disabled={actionLoading[campaign.id] === 'stop'}
                      >
                        {actionLoading[campaign.id] === 'stop' ? 'Stopping...' : 'Stop'}
                      </Button>
                    </>
                  )}
                </div>
              </div>

              {/* Video Thumbnails */}
              {campaign.thumbnails && campaign.thumbnails.length > 0 && (
                <div className="flex space-x-2 mb-4">
                  {campaign.thumbnails.slice(0, 3).map((thumbnail, index) => (
                    <img
                      key={index}
                      src={thumbnail}
                      alt={`Video ${index + 1}`}
                      className="w-16 h-12 rounded object-cover"
                    />
                  ))}
                  {campaign.thumbnails.length > 3 && (
                    <div className="w-16 h-12 bg-slate-100 rounded flex items-center justify-center text-xs text-slate-500">
                      +{campaign.thumbnails.length - 3}
                    </div>
                  )}
                </div>
              )}

              {/* Title Variants */}
              <div className="mb-4">
                <h4 className="text-sm font-medium text-slate-700 mb-2">Title Variants:</h4>
                <div className="space-y-1">
                  {campaign.titles.map((title, index) => (
                    <div key={index} className="text-sm text-slate-600 bg-slate-50 px-3 py-1 rounded">
                      {index + 1}. {title}
                    </div>
                  ))}
                </div>
              </div>

              {/* Schedule Info */}
              <div className="grid grid-cols-2 gap-4 mb-4 text-sm">
                <div>
                  <span className="text-slate-500">Interval:</span>{' '}
                  <span className="font-medium">{campaign.intervalMinutes}m</span>
                </div>
                <div>
                  <span className="text-slate-500">Duration:</span>{' '}
                  <span className="font-medium">{campaign.durationHours}h</span>
                </div>
              </div>

              {/* Next Rotation Countdown */}
              {campaign.status === 'running' && campaign.nextRotationAt && (
                <div className="mb-4">
                  <div className="flex items-center justify-between text-sm mb-2">
                    <span className="text-slate-500">Next rotation in:</span>
                    <span className="font-mono font-medium text-blue-600">
                      {getCountdown(campaign.nextRotationAt)}
                    </span>
                  </div>
                </div>
              )}

              {/* Progress Bar */}
              <div className="mb-2">
                <div className="flex items-center justify-between text-sm mb-2">
                  <span className="text-slate-500">Campaign Progress</span>
                  <span className="font-medium">{Math.round(getProgress(campaign))}%</span>
                </div>
                <Progress value={getProgress(campaign)} />
              </div>

              {/* Timeline */}
              <div className="flex items-center justify-between text-xs text-slate-500">
                <span>Started: {format(new Date(campaign.startedAt), 'MMM d, h:mm a')}</span>
                <span>Ends: {format(new Date(campaign.endsAt), 'MMM d, h:mm a')}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </Card>
  );
}