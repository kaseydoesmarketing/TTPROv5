import React, { useEffect, useState } from 'react';

export function YouTubeStatus() {
  const [status, setStatus] = useState<{connected: boolean, scope?: string, expiresAt?: string} | null>(null);

  useEffect(() => {
    (async () => {
      try {
        const res = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/oauth/google/status`, {
          credentials: 'include',
        });
        if (res.ok) setStatus(await res.json());
      } catch {}
    })();
  }, []);

  if (!status) return <div>Checking YouTube status…</div>;
  return status.connected ? (
    <div>✅ YouTube connected{status.scope ? ` (${status.scope})` : ''}{status.expiresAt ? ` – expires ${new Date(status.expiresAt).toLocaleString()}` : ''}</div>
  ) : (
    <div>❌ YouTube not connected</div>
  );
} 