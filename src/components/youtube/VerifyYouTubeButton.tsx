import React, { useState } from 'react';
import { API_BASE_URL } from '@/lib/env';

// Renders only in dev by default; enable in prod via VITE_DEBUG_YOUTUBE_VERIFY=1
const DEV_ENABLED = import.meta.env.DEV || import.meta.env.VITE_DEBUG_YOUTUBE_VERIFY === '1';

export function VerifyYouTubeButton() {
  const [result, setResult] = useState<string>('');

  if (!DEV_ENABLED) return null;

  const verify = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/api/oauth/google/verify`, { credentials: 'include' });
      const json = await res.json().catch(() => ({}));
      if (json?.ok) setResult(`ok: true${json.channelId ? `, channelId: ${json.channelId}` : ''}`);
      else setResult('ok: false');
    } catch (e) {
      setResult('error');
    }
  };

  return (
    <div className="flex items-center gap-2">
      <button onClick={verify} className="px-2 py-1 rounded bg-gray-200 text-gray-900 hover:bg-gray-300">
        Verify YouTube
      </button>
      {result && <span className="text-sm text-gray-600">{result}</span>}
    </div>
  );
} 