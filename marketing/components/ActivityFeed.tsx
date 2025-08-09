'use client'

import useSWR from 'swr';
import { formatDistanceToNow } from 'date-fns';
import Card from '@/components/ui/Card';
import Badge from '@/components/ui/Badge';
import { getCampaignActivity } from '@/lib/api';

interface ActivityItem {
  id: string;
  timestamp: string;
  type: 'campaign_created' | 'campaign_started' | 'campaign_paused' | 'campaign_resumed' | 'campaign_stopped' | 'title_rotated' | 'campaign_completed';
  message: string;
  campaignId?: string;
  metadata?: Record<string, any>;
}

export default function ActivityFeed() {
  const { data: activities, error, isLoading } = useSWR('campaign-activity', getCampaignActivity, {
    refreshInterval: 30000, // Refresh every 30 seconds
  });

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'campaign_created':
        return (
          <svg className="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
          </svg>
        );
      case 'campaign_started':
        return (
          <svg className="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.828 14.828a4 4 0 01-5.656 0M9 10h1.586a1 1 0 01.707.293l2.414 2.414a1 1 0 00.707.293H15M6 20l3-3m0 0l-3-3m3 3h12" />
          </svg>
        );
      case 'campaign_paused':
        return (
          <svg className="w-4 h-4 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 9v6m4-6v6" />
          </svg>
        );
      case 'campaign_resumed':
        return (
          <svg className="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.828 14.828a4 4 0 01-5.656 0M9 10h1.586a1 1 0 01.707.293l2.414 2.414a1 1 0 00.707.293H15" />
          </svg>
        );
      case 'campaign_stopped':
        return (
          <svg className="w-4 h-4 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 10h6v4H9z" />
          </svg>
        );
      case 'title_rotated':
        return (
          <svg className="w-4 h-4 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
        );
      case 'campaign_completed':
        return (
          <svg className="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        );
      default:
        return (
          <svg className="w-4 h-4 text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        );
    }
  };

  const getActivityBadge = (type: string) => {
    switch (type) {
      case 'campaign_created':
        return <Badge variant="info">Created</Badge>;
      case 'campaign_started':
        return <Badge variant="success">Started</Badge>;
      case 'campaign_paused':
        return <Badge variant="warning">Paused</Badge>;
      case 'campaign_resumed':
        return <Badge variant="success">Resumed</Badge>;
      case 'campaign_stopped':
        return <Badge variant="error">Stopped</Badge>;
      case 'title_rotated':
        return <Badge variant="info">Rotated</Badge>;
      case 'campaign_completed':
        return <Badge variant="success">Completed</Badge>;
      default:
        return <Badge>{type}</Badge>;
    }
  };

  if (isLoading) {
    return (
      <Card>
        <div className="space-y-4">
          <h2 className="text-lg font-semibold text-slate-900">Activity Feed</h2>
          <div className="space-y-3">
            {[1, 2, 3, 4, 5].map(i => (
              <div key={i} className="animate-pulse flex items-start space-x-3">
                <div className="w-8 h-8 bg-slate-200 rounded-full flex-shrink-0" />
                <div className="flex-1 space-y-2">
                  <div className="h-4 bg-slate-200 rounded w-3/4" />
                  <div className="h-3 bg-slate-200 rounded w-1/2" />
                </div>
              </div>
            ))}
          </div>
        </div>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <div className="space-y-4">
          <h2 className="text-lg font-semibold text-slate-900">Activity Feed</h2>
          <div className="text-center py-8">
            <p className="text-red-600">Failed to load activity feed.</p>
          </div>
        </div>
      </Card>
    );
  }

  if (!activities || activities.length === 0) {
    return (
      <Card>
        <div className="space-y-4">
          <h2 className="text-lg font-semibold text-slate-900">Activity Feed</h2>
          <div className="text-center py-8">
            <div className="w-16 h-16 bg-slate-100 rounded-full mx-auto mb-4 flex items-center justify-center">
              <svg className="w-8 h-8 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <p className="text-slate-600">No recent activity</p>
          </div>
        </div>
      </Card>
    );
  }

  return (
    <Card>
      <div className="space-y-4">
        <h2 className="text-lg font-semibold text-slate-900">Activity Feed</h2>
        
        <div className="space-y-4 max-h-96 overflow-y-auto">
          {activities.map((activity: ActivityItem) => (
            <div key={activity.id} className="flex items-start space-x-3">
              <div className="flex-shrink-0 w-8 h-8 bg-slate-100 rounded-full flex items-center justify-center">
                {getActivityIcon(activity.type)}
              </div>
              
              <div className="flex-1 min-w-0">
                <div className="flex items-center space-x-2 mb-1">
                  {getActivityBadge(activity.type)}
                  <span className="text-xs text-slate-500">
                    {formatDistanceToNow(new Date(activity.timestamp), { addSuffix: true })}
                  </span>
                </div>
                
                <p className="text-sm text-slate-700">
                  {activity.message}
                </p>
                
                {activity.metadata && (
                  <div className="mt-2">
                    {Object.entries(activity.metadata).map(([key, value]) => (
                      <div key={key} className="text-xs text-slate-500">
                        <span className="font-medium">{key}:</span> {String(value)}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </Card>
  );
}