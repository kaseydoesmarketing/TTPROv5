import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Badge } from './ui/badge';
import { 
  LineChart, 
  Line, 
  AreaChart, 
  Area, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import { TrendingUp, Eye, ThumbsUp, Users, Video } from 'lucide-react';

interface AnalyticsData {
  performance: Array<{
    date: string;
    views: number;
    engagement: number;
    clickRate: number;
  }>;
  testResults: Array<{
    test: string;
    variant_a: number;
    variant_b: number;
    winner: string;
  }>;
  channelStats: {
    totalViews: number;
    totalEngagement: number;
    avgClickRate: number;
    testsCompleted: number;
  };
}

const mockData: AnalyticsData = {
  performance: [
    { date: '2024-01-01', views: 1200, engagement: 85, clickRate: 4.2 },
    { date: '2024-01-02', views: 1350, engagement: 92, clickRate: 4.8 },
    { date: '2024-01-03', views: 1180, engagement: 78, clickRate: 3.9 },
    { date: '2024-01-04', views: 1420, engagement: 105, clickRate: 5.1 },
    { date: '2024-01-05', views: 1580, engagement: 118, clickRate: 5.7 },
    { date: '2024-01-06', views: 1650, engagement: 125, clickRate: 6.2 },
    { date: '2024-01-07', views: 1480, engagement: 98, clickRate: 4.9 }
  ],
  testResults: [
    { test: 'Ultimate Guide to...', variant_a: 1200, variant_b: 1580, winner: 'B' },
    { test: 'Top 10 Tips for...', variant_a: 980, variant_b: 850, winner: 'A' },
    { test: 'How to Master...', variant_a: 1350, variant_b: 1420, winner: 'B' },
    { test: 'Secret Formula...', variant_a: 760, variant_b: 920, winner: 'B' }
  ],
  channelStats: {
    totalViews: 45280,
    totalEngagement: 3420,
    avgClickRate: 4.8,
    testsCompleted: 12
  }
};

const COLORS = ['#8884d8', '#82ca9d', '#ffc658', '#ff7c7c'];

export function AnalyticsDashboard() {
  const [data] = useState<AnalyticsData>(mockData);
  const [selectedPeriod, setSelectedPeriod] = useState('7d');

  const formatNumber = (num: number) => {
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
    if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
    return num.toString();
  };

  return (
    <div className="space-y-6">
      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card className="border-none shadow-lg bg-gradient-to-r from-blue-50 to-blue-100">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-blue-700">Total Views</CardTitle>
            <Eye className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-900">
              {formatNumber(data.channelStats.totalViews)}
            </div>
            <p className="text-xs text-blue-600 flex items-center mt-1">
              <TrendingUp className="h-3 w-3 mr-1" />
              +12.5% from last month
            </p>
          </CardContent>
        </Card>

        <Card className="border-none shadow-lg bg-gradient-to-r from-green-50 to-green-100">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-green-700">Engagement</CardTitle>
            <ThumbsUp className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-900">
              {formatNumber(data.channelStats.totalEngagement)}
            </div>
            <p className="text-xs text-green-600 flex items-center mt-1">
              <TrendingUp className="h-3 w-3 mr-1" />
              +8.2% from last month
            </p>
          </CardContent>
        </Card>

        <Card className="border-none shadow-lg bg-gradient-to-r from-purple-50 to-purple-100">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-purple-700">Avg Click Rate</CardTitle>
            <Users className="h-4 w-4 text-purple-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-purple-900">
              {data.channelStats.avgClickRate}%
            </div>
            <p className="text-xs text-purple-600 flex items-center mt-1">
              <TrendingUp className="h-3 w-3 mr-1" />
              +0.8% from last month
            </p>
          </CardContent>
        </Card>

        <Card className="border-none shadow-lg bg-gradient-to-r from-orange-50 to-orange-100">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-orange-700">Tests Completed</CardTitle>
            <Video className="h-4 w-4 text-orange-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-900">
              {data.channelStats.testsCompleted}
            </div>
            <p className="text-xs text-orange-600 flex items-center mt-1">
              <TrendingUp className="h-3 w-3 mr-1" />
              +4 this month
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Charts */}
      <Tabs defaultValue="performance" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="performance">Performance</TabsTrigger>
          <TabsTrigger value="tests">Test Results</TabsTrigger>
          <TabsTrigger value="trends">Trends</TabsTrigger>
        </TabsList>

        <TabsContent value="performance" className="space-y-6">
          <Card className="shadow-lg">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Performance Overview</CardTitle>
                  <CardDescription>
                    Track views, engagement, and click-through rates over time
                  </CardDescription>
                </div>
                <Badge variant="secondary">Last 7 days</Badge>
              </div>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={400}>
                <LineChart data={data.performance}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis yAxisId="left" />
                  <YAxis yAxisId="right" orientation="right" />
                  <Tooltip />
                  <Legend />
                  <Line 
                    yAxisId="left" 
                    type="monotone" 
                    dataKey="views" 
                    stroke="#8884d8" 
                    strokeWidth={2}
                    name="Views"
                  />
                  <Line 
                    yAxisId="left" 
                    type="monotone" 
                    dataKey="engagement" 
                    stroke="#82ca9d" 
                    strokeWidth={2}
                    name="Engagement"
                  />
                  <Line 
                    yAxisId="right" 
                    type="monotone" 
                    dataKey="clickRate" 
                    stroke="#ffc658" 
                    strokeWidth={2}
                    name="Click Rate (%)"
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="tests" className="space-y-6">
          <Card className="shadow-lg">
            <CardHeader>
              <CardTitle>A/B Test Results</CardTitle>
              <CardDescription>
                Compare performance between title variants
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={400}>
                <BarChart data={data.testResults}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="test" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="variant_a" fill="#8884d8" name="Variant A" />
                  <Bar dataKey="variant_b" fill="#82ca9d" name="Variant B" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="trends" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card className="shadow-lg">
              <CardHeader>
                <CardTitle>Views Trend</CardTitle>
                <CardDescription>
                  View count progression over time
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <AreaChart data={data.performance}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip />
                    <Area 
                      type="monotone" 
                      dataKey="views" 
                      stroke="#8884d8" 
                      fill="#8884d8" 
                      fillOpacity={0.3}
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <Card className="shadow-lg">
              <CardHeader>
                <CardTitle>Test Winners Distribution</CardTitle>
                <CardDescription>
                  Which variants perform better
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={[
                        { name: 'Variant A Wins', value: 3, color: '#8884d8' },
                        { name: 'Variant B Wins', value: 9, color: '#82ca9d' }
                      ]}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {[
                        { name: 'Variant A Wins', value: 3, color: '#8884d8' },
                        { name: 'Variant B Wins', value: 9, color: '#82ca9d' }
                      ].map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}