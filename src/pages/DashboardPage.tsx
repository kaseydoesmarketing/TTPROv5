import { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { apiClient } from '@/lib/api-auth0';
import { toast } from 'sonner';
import { BarChart3, TestTube, Youtube, TrendingUp } from 'lucide-react';

export function DashboardPage() {
  const [stats, setStats] = useState({
    totalTests: 0,
    activeTests: 0,
    totalChannels: 0,
    improvement: 0
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      setLoading(true);
      // In a real app, this would fetch from /dashboard/stats endpoint
      const [tests, channels] = await Promise.all([
        apiClient.getABTests().catch(() => []),
        apiClient.getChannels().catch(() => [])
      ]);

      setStats({
        totalTests: tests.length || 0,
        activeTests: tests.filter((t: any) => t.status === 'active').length || 0,
        totalChannels: channels.length || 0,
        improvement: 12.5 // Mock data
      });
    } catch (error) {
      console.error('Dashboard error:', error);
      toast.error('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const statsCards = [
    {
      title: 'Total A/B Tests',
      value: stats.totalTests,
      description: 'All time tests created',
      icon: TestTube,
      color: 'text-blue-600'
    },
    {
      title: 'Active Tests',
      value: stats.activeTests,
      description: 'Currently running',
      icon: BarChart3,
      color: 'text-green-600'
    },
    {
      title: 'Connected Channels',
      value: stats.totalChannels,
      description: 'YouTube channels',
      icon: Youtube,
      color: 'text-red-600'
    },
    {
      title: 'Avg. Improvement',
      value: `${stats.improvement}%`,
      description: 'Performance gain',
      icon: TrendingUp,
      color: 'text-purple-600'
    }
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-muted-foreground mt-2">
          Monitor your YouTube title optimization performance
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {statsCards.map((stat) => {
          const Icon = stat.icon;
          return (
            <Card key={stat.title}>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">
                  {stat.title}
                </CardTitle>
                <Icon className={`h-4 w-4 ${stat.color}`} />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stat.value}</div>
                <p className="text-xs text-muted-foreground">
                  {stat.description}
                </p>
              </CardContent>
            </Card>
          );
        })}
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Getting Started</CardTitle>
          <CardDescription>
            Follow these steps to optimize your YouTube titles
          </CardDescription>
        </CardHeader>
        <CardContent>
          <ol className="list-decimal list-inside space-y-2">
            <li>Connect your YouTube channel in the Channels section</li>
            <li>Create your first A/B test with different title variations</li>
            <li>Let the test run for at least 48 hours</li>
            <li>Review results and apply the winning title</li>
          </ol>
        </CardContent>
      </Card>
    </div>
  );
}