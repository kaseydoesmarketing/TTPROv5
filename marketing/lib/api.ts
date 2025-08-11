import { authenticatedFetch } from './authHandshake';

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || 'https://ttprov5.onrender.com';

export async function apiFetch(path: string, opts: RequestInit = {}) {
  const url = `${API_BASE}${path}`;
  
  // Use authenticatedFetch for automatic token refresh on 401
  const response = await authenticatedFetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...opts.headers,
    },
    ...opts,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Network error' }));
    throw new Error(error.detail || `HTTP error! status: ${response.status}`);
  }

  return response.json();
}

// Auth
export async function postIdToken(idToken: string) {
  return apiFetch('/api/auth/firebase', {
    method: 'POST',
    body: JSON.stringify({ idToken }),
  });
}

// Campaigns
export async function getCampaigns() {
  return apiFetch('/api/campaigns');
}

export async function getCampaignKpis() {
  return apiFetch('/api/campaigns/kpis');
}

export async function getCampaignActivity() {
  return apiFetch('/api/campaigns/activity');
}

export async function createCampaign(data: {
  channelId: string;
  videoIds: string[];
  titles: string[];
  intervalMinutes: number;
  durationHours: number;
}) {
  return apiFetch('/api/campaigns', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function pauseCampaign(id: string) {
  return apiFetch(`/api/campaigns/${id}/pause`, {
    method: 'POST',
  });
}

export async function resumeCampaign(id: string) {
  return apiFetch(`/api/campaigns/${id}/resume`, {
    method: 'POST',
  });
}

export async function stopCampaign(id: string) {
  return apiFetch(`/api/campaigns/${id}/stop`, {
    method: 'POST',
  });
}

// YouTube
export async function getYouTubeChannels() {
  return apiFetch('/api/youtube/channels');
}

export async function getYouTubeVideos(params: { q?: string; page?: string } = {}) {
  const searchParams = new URLSearchParams();
  if (params.q) searchParams.append('q', params.q);
  if (params.page) searchParams.append('page', params.page);
  
  const query = searchParams.toString();
  return apiFetch(`/api/youtube/videos${query ? '?' + query : ''}`);
}

// Billing
export async function createBillingPortalSession() {
  return apiFetch('/api/billing/portal', {
    method: 'POST',
  });
}

// Health
export async function getHealth() {
  return apiFetch('/health');
}