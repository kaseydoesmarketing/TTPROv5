import React, { useEffect, useState } from 'react';
import { API_BASE_URL } from '@/lib/env';

type Status = { connected: boolean; scope?: string; expiresAt?: string };

export function YouTubeStatus() {
  const [status, setStatus] = useState<Status | null>(null);

  useEffect(() => {
    (async () => {
      try {
        const res = await fetch(`${API_BASE_URL}/api/oauth/google/status`, { credentials: 'include' });
        setStatus(res.ok ? await res.json() : { connected: false });
      } catch {
        setStatus({ connected: false });
      }
    })();
  }, []);

  if (!status) return <div>Checking YouTube status…</div>;
  return status.connected ? (
    <div>✅ YouTube connected{status.scope ? ` (${status.scope})` : ''}{status.expiresAt ? ` — expires ${new Date(status.expiresAt).toLocaleString()}` : ''}</div>
  ) : (
    <div>❌ YouTube not connected</div>
  );
} 