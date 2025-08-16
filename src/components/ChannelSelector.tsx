import React, { useEffect, useState } from 'react';
import { API_BASE_URL } from '@/lib/env';

interface Channel {
  id: string
  title: string
}

export function ChannelSelector() {
  const [channels, setChannels] = useState<Channel[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const fetchJson = async (path: string, init?: RequestInit) => {
    const res = await fetch(`${API_BASE_URL}${path}`, { credentials: 'include', ...(init || {}) })
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    return res.json()
  }

  useEffect(() => {
    const run = async () => {
      try {
        setLoading(true)
        const data = await fetchJson('/api/channels')
        setChannels(data.channels || [])
      } catch (e) {
        setError(e instanceof Error ? e.message : 'Failed to load channels')
      } finally {
        setLoading(false)
      }
    }
    run()
  }, [])

  const sync = async () => {
    try {
      await fetchJson('/api/channels/sync', { method: 'POST' })
      const data = await fetchJson('/api/channels')
      setChannels(data.channels || [])
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to sync channels')
    }
  }

  if (loading) return <div>Loading…</div>
  if (error) return <div className="text-red-600">{error}</div>

  return (
    <div>
      <button onClick={sync} className="px-2 py-1 bg-gray-200 rounded">Sync Channels</button>
      <ul>
        {channels.map(c => <li key={c.id}>{c.title}</li>)}
      </ul>
    </div>
  )
}
