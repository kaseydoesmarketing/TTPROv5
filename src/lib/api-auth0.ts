const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;
if (!API_BASE_URL) {
  throw new Error('[env] VITE_API_BASE_URL is missing. Set it (e.g. https://ttprov5.onrender.com)');
}

export class ApiClient {
  private async fetchWithSession(url: string, options: RequestInit = {}) {
    const headers = {
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    } as Record<string, string>;

    const response = await fetch(`${API_BASE_URL}${url}`, {
      ...options,
      headers,
      credentials: 'include',
    });

    if (!response.ok) {
      if (response.status === 401) {
        window.location.href = '/login';
        throw new Error('Session expired');
      }
      const error = await response.json().catch(() => ({ detail: 'Network error' }));
      throw new Error(error.detail || `HTTP ${response.status}`);
    }

    const text = await response.text();
    return text ? JSON.parse(text) : null;
  }

  async checkHealth() {
    const response = await fetch(`${API_BASE_URL}/api/healthz`, { credentials: 'include' });
    return response.ok;
  }

  async getCurrentUser() {
    return this.fetchWithSession('/api/auth/me');
  }

  async logout() {
    return this.fetchWithSession('/api/auth/logout', { method: 'POST' });
  }

  async getChannels() {
    return this.fetchWithSession('/api/channels');
  }

  async addChannel(channelData: any) {
    return this.fetchWithSession('/api/channels', { method: 'POST', body: JSON.stringify(channelData) });
  }

  async getChannelVideos(maxResults: number = 50) {
    return this.fetchWithSession(`/api/ab-tests/channel/videos?max_results=${maxResults}`);
  }

  async syncChannels() {
    return this.fetchWithSession('/api/channels/sync', { method: 'POST' });
  }

  async getABTests() {
    return this.fetchWithSession('/api/ab-tests');
  }

  async createABTest(testData: any) {
    return this.fetchWithSession('/api/ab-tests', { method: 'POST', body: JSON.stringify(testData) });
  }

  async updateABTest(testId: string, testData: any) {
    return this.fetchWithSession(`/api/ab-tests/${testId}`, { method: 'PUT', body: JSON.stringify(testData) });
  }

  async deleteABTest(testId: string) {
    return this.fetchWithSession(`/api/ab-tests/${testId}`, { method: 'DELETE' });
  }

  async getBillingStatus() {
    return this.fetchWithSession('/api/billing/status');
  }

  async createCheckoutSession(priceId: string) {
    return this.fetchWithSession('/api/billing/create-checkout-session', { method: 'POST', body: JSON.stringify({ price_id: priceId }) });
  }

  async cancelSubscription() {
    return this.fetchWithSession('/api/billing/cancel-subscription', { method: 'POST' });
  }

  async getUsageStats() {
    return this.fetchWithSession('/api/billing/usage');
  }
}

export const apiClient = new ApiClient();