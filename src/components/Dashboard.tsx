import { useState, useEffect } from 'react';
import { useAuthContext } from '../contexts/Auth0Context';
import { CreateTestModal } from './CreateTestModal';
import { TestList } from './TestList';
import { ChannelSelector } from './ChannelSelector';
import { apiClient } from '../lib/api-auth0';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Avatar, AvatarFallback, AvatarImage } from './ui/avatar';
import { Badge } from './ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Play, TrendingUp, CheckCircle, Clock, Plus, BarChart3, Settings } from 'lucide-react';
import { AnalyticsDashboard } from './AnalyticsDashboard';

export function Dashboard() {
  const { user, logout } = useAuthContext();
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const [stats, setStats] = useState({
    activeTests: 0,
    completedTests: 0,
    quotaUsed: 0
  });

  const handleLogout = async () => {
    try {
      await logout();
    } catch (error) {
      console.error('Failed to log out:', error);
    }
  };

  const handleTestCreated = () => {
    setRefreshTrigger(prev => prev + 1);
    fetchStats();
  };

  const fetchStats = async () => {
    try {
      if (!user) {
        console.error('No authenticated user available for API request');
        return;
      }

      const tests = await apiClient.getABTests();
      
      if (tests && Array.isArray(tests)) {
        const activeTests = tests.filter((test: { status: string }) => test.status === 'active').length;
        const completedTests = tests.filter((test: { status: string }) => test.status === 'completed').length;
        
        setStats({
          activeTests,
          completedTests,
          quotaUsed: 0
        });
      }
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    }
  };

  useEffect(() => {
    fetchStats();
  }, [refreshTrigger]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      <nav className="bg-white/80 backdrop-blur-sm shadow-sm border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <Play className="h-8 w-8 text-primary" />
                <h1 className="text-xl font-bold text-gray-900">TitleTesterPro</h1>
              </div>
            </div>
            <div className="flex items-center space-x-6">
              <ChannelSelector />
              <div className="flex items-center space-x-3">
                <Avatar className="h-8 w-8">
                  <AvatarImage src={user?.picture || ''} alt="Profile" />
                  <AvatarFallback>{user?.name?.charAt(0) || 'U'}</AvatarFallback>
                </Avatar>
                <span className="text-sm font-medium text-gray-700">{user?.name}</span>
              </div>
              <Button variant="ghost" size="sm" onClick={handleLogout}>
                Sign Out
              </Button>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto py-8 sm:px-6 lg:px-8">
        <div className="px-4 sm:px-0">
          <div className="mb-8">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-3xl font-bold text-gray-900 mb-2">Dashboard</h2>
                <p className="text-muted-foreground">Track your A/B tests and optimize your YouTube titles for better performance.</p>
              </div>
              <div className="flex items-center space-x-3">
                <Button variant="outline" size="sm">
                  <Settings className="h-4 w-4 mr-2" />
                  Settings
                </Button>
                <Button onClick={() => setShowCreateModal(true)}>
                  <Plus className="h-4 w-4 mr-2" />
                  Create Test
                </Button>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <Card className="border-none shadow-lg bg-gradient-to-r from-blue-50 to-blue-100 border-blue-200">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-blue-700">Active Tests</CardTitle>
                <Clock className="h-4 w-4 text-blue-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-blue-900">{stats.activeTests}</div>
                <p className="text-xs text-blue-600">
                  {stats.activeTests === 0 ? 'No active tests' : `${stats.activeTests} running`}
                </p>
              </CardContent>
            </Card>

            <Card className="border-none shadow-lg bg-gradient-to-r from-green-50 to-green-100 border-green-200">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-green-700">Completed Tests</CardTitle>
                <CheckCircle className="h-4 w-4 text-green-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-green-900">{stats.completedTests}</div>
                <p className="text-xs text-green-600">
                  {stats.completedTests === 0 ? 'No completed tests' : `${stats.completedTests} finished`}
                </p>
              </CardContent>
            </Card>

            <Card className="border-none shadow-lg bg-gradient-to-r from-purple-50 to-purple-100 border-purple-200">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-purple-700">API Quota</CardTitle>
                <BarChart3 className="h-4 w-4 text-purple-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-purple-900">{stats.quotaUsed}%</div>
                <p className="text-xs text-purple-600">
                  {stats.quotaUsed} / 10,000 daily quota
                </p>
              </CardContent>
            </Card>
          </div>

          <Tabs defaultValue="overview" className="w-full">
            <TabsList className="grid w-full grid-cols-2 mb-6">
              <TabsTrigger value="overview">Overview</TabsTrigger>
              <TabsTrigger value="analytics">Analytics</TabsTrigger>
            </TabsList>
            
            <TabsContent value="overview" className="space-y-6">
              <Card className="shadow-lg border-none">
                <CardHeader className="bg-gradient-to-r from-slate-50 to-slate-100 border-b">
                  <div className="flex justify-between items-center">
                    <div>
                      <CardTitle className="text-xl text-gray-900">Your A/B Tests</CardTitle>
                      <CardDescription className="mt-1">
                        Monitor and manage your title optimization experiments
                      </CardDescription>
                    </div>
                    <Badge variant="secondary" className="text-xs">
                      {stats.activeTests + stats.completedTests} total tests
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent className="p-6">
                  <TestList refreshTrigger={refreshTrigger} />
                </CardContent>
              </Card>

              {(stats.activeTests + stats.completedTests) === 0 && (
                <Card className="shadow-lg border-none bg-gradient-to-r from-orange-50 to-amber-50">
                  <CardHeader>
                    <CardTitle className="flex items-center text-orange-800">
                      <TrendingUp className="h-5 w-5 mr-2" />
                      Getting Started
                    </CardTitle>
                    <CardDescription className="text-orange-700">
                      Create your first A/B test to start optimizing your YouTube titles
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <p className="text-sm text-orange-700">
                        Follow these steps to get started with TitleTesterPro:
                      </p>
                      <ol className="list-decimal list-inside text-sm text-orange-700 space-y-2 ml-4">
                        <li>Connect your YouTube channel</li>
                        <li>Select a video to test</li>
                        <li>Create title variants</li>
                        <li>Set test duration and rotation schedule</li>
                        <li>Monitor results and optimize</li>
                      </ol>
                      <div className="pt-4">
                        <Button 
                          onClick={() => setShowCreateModal(true)}
                          className="bg-orange-600 hover:bg-orange-700"
                        >
                          <Plus className="h-4 w-4 mr-2" />
                          Create Your First Test
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )}
            </TabsContent>
            
            <TabsContent value="analytics" className="space-y-6">
              <AnalyticsDashboard />
            </TabsContent>
          </Tabs>
        </div>
      </main>

      <CreateTestModal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        onTestCreated={handleTestCreated}
      />
    </div>
  );
}
