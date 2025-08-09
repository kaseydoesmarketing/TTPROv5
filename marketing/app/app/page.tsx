'use client'

import AuthGate from '@/components/AuthGate';
import TTProDashboard from '@/components/TTProDashboard';

export default function AppPage() {
  return (
    <AuthGate>
      <TTProDashboard />
    </AuthGate>
  );
}