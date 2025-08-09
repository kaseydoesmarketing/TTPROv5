'use client'

import { useEffect, useState } from 'react';
import { getHealth } from '@/lib/api';

export default function ApiStatus() {
  const [status, setStatus] = useState<'healthy' | 'degraded' | 'down'>('healthy');
  const [lastCheck, setLastCheck] = useState<Date | null>(null);

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const health = await getHealth();
        setStatus(health.status === 'healthy' ? 'healthy' : 'degraded');
        setLastCheck(new Date());
      } catch (error) {
        setStatus('down');
        setLastCheck(new Date());
      }
    };

    // Initial check
    checkHealth();

    // Check every 15 seconds
    const interval = setInterval(checkHealth, 15000);

    return () => clearInterval(interval);
  }, []);

  const getStatusColor = () => {
    switch (status) {
      case 'healthy':
        return 'bg-green-100 text-green-800';
      case 'degraded':
        return 'bg-yellow-100 text-yellow-800';
      case 'down':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusDot = () => {
    switch (status) {
      case 'healthy':
        return 'bg-green-500';
      case 'degraded':
        return 'bg-yellow-500';
      case 'down':
        return 'bg-red-500';
      default:
        return 'bg-gray-500';
    }
  };

  return (
    <div className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium ${getStatusColor()}`}>
      <div className={`w-2 h-2 rounded-full mr-2 ${getStatusDot()}`} />
      <span className="capitalize">{status}</span>
    </div>
  );
}