'use client'

import { useState } from 'react';
import { User } from 'firebase/auth';
import { auth, logout } from '@/lib/firebaseClient';
import { Button } from '@/components/ui/button';
import Kpis from '@/components/Kpis';
import LiveCampaigns from '@/components/LiveCampaigns';
import ActivityFeed from '@/components/ActivityFeed';
import ApiStatus from '@/components/ApiStatus';
import BillingPortalButton from '@/components/BillingPortalButton';
import NewCampaignWizard from '@/components/NewCampaignWizard';

export default function TTProDashboard() {
  const [showNewCampaignModal, setShowNewCampaignModal] = useState(false);
  const user = auth.currentUser;

  const handleSignOut = async () => {
    try {
      await logout();
    } catch (error) {
      console.error('Failed to sign out:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-slate-200">
        <div className="bg-gradient-to-r from-blue-500 to-fuchsia-500 h-1" />
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo & Brand */}
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-gradient-to-r from-blue-600 to-fuchsia-600 rounded-lg flex items-center justify-center">
                <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 3l14 9-14 9V3z" />
                </svg>
              </div>
              <div>
                <h1 className="text-lg font-semibold text-slate-900">TitleTesterPro</h1>
                <p className="text-xs text-slate-500">Dashboard v5.0</p>
              </div>
            </div>

            {/* Right Side */}
            <div className="flex items-center space-x-4">
              <ApiStatus />
              
              {user && (
                <div className="flex items-center space-x-3">
                  <img
                    src={user.photoURL || '/default-avatar.png'}
                    alt={user.displayName || 'User'}
                    className="w-8 h-8 rounded-full"
                  />
                  <span className="text-sm font-medium text-slate-700 hidden sm:block">
                    {user.displayName}
                  </span>
                </div>
              )}
              
              <Button variant="outline" size="sm" onClick={handleSignOut}>
                Sign Out
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* KPIs Row */}
        <div className="mb-8">
          <Kpis />
        </div>

        {/* Action Row */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h2 className="text-2xl font-bold text-slate-900">Campaigns</h2>
            <p className="text-slate-600">Manage your A/B testing campaigns</p>
          </div>
          
          <Button 
            onClick={() => setShowNewCampaignModal(true)}
            className="flex items-center space-x-2"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
            </svg>
            <span>New Campaign</span>
          </Button>
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column - Live Campaigns */}
          <div className="lg:col-span-2">
            <LiveCampaigns />
          </div>

          {/* Right Column - Activity Feed */}
          <div className="lg:col-span-1">
            <ActivityFeed />
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-slate-200 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-6">
              <BillingPortalButton />
              <span className="text-xs text-slate-500">v5.0</span>
            </div>
            
            <div className="text-xs text-slate-500">
              &copy; 2024 TitleTesterPro. All rights reserved.
            </div>
          </div>
        </div>
      </footer>

      {/* New Campaign Modal */}
      <NewCampaignWizard
        isOpen={showNewCampaignModal}
        onClose={() => setShowNewCampaignModal(false)}
      />
    </div>
  );
}