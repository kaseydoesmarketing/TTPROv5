import { auth } from './firebase';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export class ApiClient {
  private async getAuthToken(): Promise<string | null> {
    const user = auth.currentUser;
    if (!user) return null;
    return user.getIdToken();
  }

  private async fetchWithAuth(url: string, options: RequestInit = {}) {
    const token = await this.getAuthToken();
    
    const headers = {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    };

    const response = await fetch(`${API_BASE_URL}${url}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Network error' }));
      throw new Error(error.detail || `HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  // Auth endpoints
  async getCurrentUser() {
    return this.fetchWithAuth('/auth/me');
  }

  async completeOAuth(code: string, state: string) {
    return this.fetchWithAuth('/auth/oauth/complete', {
      method: 'POST',
      body: JSON.stringify({ code, state }),
    });
  }

  // Channel endpoints
  async getChannels() {
    return this.fetchWithAuth('/channels');
  }

  async addChannel(channelData: any) {
    return this.fetchWithAuth('/channels', {
      method: 'POST',
      body: JSON.stringify(channelData),
    });
  }

  async getChannelVideos(maxResults: number = 50) {
    return this.fetchWithAuth(`/api/ab-tests/channel/videos?max_results=${maxResults}`);
  }

  async syncChannels() {
    return this.fetchWithAuth('/api/channels/sync', {
      method: 'POST',
    });
  }

  // A/B Test endpoints
  async getABTests() {
    return this.fetchWithAuth('/ab-tests');
  }

  async createABTest(testData: any) {
    return this.fetchWithAuth('/ab-tests', {
      method: 'POST',
      body: JSON.stringify(testData),
    });
  }

  async updateABTest(testId: string, testData: any) {
    return this.fetchWithAuth(`/ab-tests/${testId}`, {
      method: 'PUT',
      body: JSON.stringify(testData),
    });
  }

  async deleteABTest(testId: string) {
    return this.fetchWithAuth(`/ab-tests/${testId}`, {
      method: 'DELETE',
    });
  }

  // Billing endpoints
  async getBillingStatus() {
    return this.fetchWithAuth('/billing/status');
  }

  async createCheckoutSession(priceId: string) {
    return this.fetchWithAuth('/billing/create-checkout-session', {
      method: 'POST',
      body: JSON.stringify({ price_id: priceId }),
    });
  }

  // Health check
  async healthCheck() {
    const response = await fetch(`${API_BASE_URL}/health`);
    return response.json();
  }
}

export const apiClient = new ApiClient();