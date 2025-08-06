import { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { CreateTestModal } from './CreateTestModal';
import { TestList } from './TestList';
import { ChannelSelector } from './ChannelSelector';
import { apiClient } from '../lib/api';

export function Dashboard() {
  const { currentUser, logout } = useAuth();
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
      if (!currentUser) {
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
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-bold text-gray-900">TitleTesterPro</h1>
            </div>
            <div className="flex items-center space-x-4">
              <ChannelSelector />
              <div className="flex items-center space-x-2">
                {currentUser?.photoURL && (
                  <img
                    src={currentUser.photoURL}
                    alt="Profile"
                    className="w-8 h-8 rounded-full"
                  />
                )}
                <span className="text-sm text-gray-700">{currentUser?.displayName}</span>
              </div>
              <button
                onClick={handleLogout}
                className="text-sm text-gray-500 hover:text-gray-700"
              >
                Sign Out
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Welcome to TitleTesterPro</h2>
            <p className="text-gray-600">Start A/B testing your YouTube titles to maximize engagement and views.</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 bg-blue-500 rounded-md flex items-center justify-center">
                      <span className="text-white font-bold">A</span>
                    </div>
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">Active Tests</dt>
                      <dd className="text-lg font-medium text-gray-900">{stats.activeTests}</dd>
                    </dl>
                  </div>
                </div>
                <div className="mt-3">
                  <div className="text-sm text-gray-500">
                    {stats.activeTests === 0 ? 'No active tests' : `${stats.activeTests} running`}
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 bg-green-500 rounded-md flex items-center justify-center">
                      <span className="text-white font-bold">✓</span>
                    </div>
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">Completed Tests</dt>
                      <dd className="text-lg font-medium text-gray-900">{stats.completedTests}</dd>
                    </dl>
                  </div>
                </div>
                <div className="mt-3">
                  <div className="text-sm text-gray-500">
                    {stats.completedTests === 0 ? 'No completed tests' : `${stats.completedTests} finished`}
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 bg-purple-500 rounded-md flex items-center justify-center">
                      <span className="text-white font-bold">%</span>
                    </div>
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">API Quota Used</dt>
                      <dd className="text-lg font-medium text-gray-900">{stats.quotaUsed}%</dd>
                    </dl>
                  </div>
                </div>
                <div className="mt-3">
                  <div className="text-sm text-gray-500">{stats.quotaUsed} / 10,000 daily quota</div>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white shadow rounded-lg mb-8">
            <div className="px-4 py-5 sm:p-6">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg leading-6 font-medium text-gray-900">Your A/B Tests</h3>
                <button
                  onClick={() => setShowCreateModal(true)}
                  className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
                >
                  Create New Test
                </button>
              </div>
              <TestList refreshTrigger={refreshTrigger} />
            </div>
          </div>

          <div className="bg-white shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">Getting Started</h3>
              <div className="text-sm text-gray-600 mb-4">
                Create your first A/B test to start optimizing your YouTube titles
              </div>
              <div className="text-sm text-gray-600 mb-6">
                To get started with TitleTesterPro:
                <ol className="list-decimal list-inside mt-2 space-y-1">
                  <li>Connect your YouTube channel (coming soon)</li>
                  <li>Select a video to test</li>
                  <li>Create title variants</li>
                  <li>Set test duration and rotation schedule</li>
                  <li>Monitor results and optimize</li>
                </ol>
              </div>
            </div>
          </div>
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
