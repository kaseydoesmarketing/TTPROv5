'use client'

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { createBillingPortalSession } from '@/lib/api';

export default function BillingPortalButton() {
  const [isLoading, setIsLoading] = useState(false);

  const handleOpenPortal = async () => {
    setIsLoading(true);
    
    try {
      const { url } = await createBillingPortalSession();
      window.location.href = url;
    } catch (error) {
      console.error('Failed to open billing portal:', error);
      // Could show a toast notification here
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Button 
      variant="outline" 
      onClick={handleOpenPortal}
      disabled={isLoading}
      className="flex items-center space-x-2"
    >
      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
      </svg>
      <span>{isLoading ? 'Opening...' : 'Manage Billing'}</span>
    </Button>
  );
}