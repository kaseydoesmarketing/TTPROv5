// src/lib/api-client.ts
const RAW_BASE = import.meta.env.VITE_API_BASE_URL;

if (!RAW_BASE) {
  throw new Error(
    '[env] VITE_API_BASE_URL is missing. Set it to your v5 API, e.g. https://ttprov5.onrender.com'
  );
}

const API_BASE_URL = (() => {
  let b = RAW_BASE.trim();
  if (typeof window !== 'undefined') {
    const h = window.location.hostname;
    if (/titletesterpro\.com$/.test(h) && /onrender\.com/.test(b)) {
      // Prefer same-origin. Return empty base so paths like '/api/...'
      // remain relative to the current origin.
      return '';
    }
  }
  if (b.startsWith('http://') && /onrender\.com/.test(b)) b = b.replace(/^http:\/\//, 'https://');
  return b.replace(/\/$/, '');
})();

function join(base: string, path: string): string {
  if (!base) return path; // same-origin
  // Avoid double '/api' when base ends with '/api' and path starts with '/api'
  if (/\/api$/.test(base) && path.startsWith('/api')) return base + path.replace(/^\/api/, '');
  return base + path;
}

async function fetchJson(path: string, options: RequestInit = {}) {
  const res = await fetch(join(API_BASE_URL, path), {
    credentials: 'include',
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    },
  });
  if (!res.ok) {
    const text = await res.text().catch(() => '');
    throw new Error(`API ${path} ${res.status}: ${text}`);
  }
  const text = await res.text();
  return text ? JSON.parse(text) : null;
}

export const apiClient = {
  // Auth
  async getSession() {
    return fetchJson('/api/auth/session', { method: 'GET' });
  },
  async logout() {
    return fetchJson('/api/auth/logout', { method: 'POST' });
  },

  // Channels
  async getChannels() {
    return fetchJson('/api/channels');
  },
  async addChannel(channelData: any) {
    return fetchJson('/api/channels', { method: 'POST', body: JSON.stringify(channelData) });
  },
  async syncChannels() {
    return fetchJson('/api/channels/sync', { method: 'POST' });
  },
  async getChannelVideos(maxResults: number = 50) {
    return fetchJson(`/api/ab-tests/channel/videos?max_results=${maxResults}`);
  },

  // A/B Tests
  async getABTests() {
    return fetchJson('/api/ab-tests');
  },
  async createABTest(testData: any) {
    return fetchJson('/api/ab-tests', { method: 'POST', body: JSON.stringify(testData) });
  },
  async updateABTest(testId: string, testData: any) {
    return fetchJson(`/api/ab-tests/${testId}`, { method: 'PUT', body: JSON.stringify(testData) });
  },
  async deleteABTest(testId: string) {
    return fetchJson(`/api/ab-tests/${testId}`, { method: 'DELETE' });
  },

  // Billing
  async getBillingStatus() {
    return fetchJson('/api/billing/status');
  },
  async createCheckoutSession(priceId: string) {
    return fetchJson('/api/billing/create-checkout-session', {
      method: 'POST',
      body: JSON.stringify({ price_id: priceId }),
    });
  },
  async cancelSubscription() {
    return fetchJson('/api/billing/cancel-subscription', { method: 'POST' });
  },
}; 