const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://ttprov5.onrender.com';

export class ApiClient {
  private async fetchWithSession(url: string, options: RequestInit = {}) {
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    const response = await fetch(`${API_BASE_URL}${url}`, {
      ...options,
      headers,
      credentials: 'include', // Always include cookies for session-based auth
    });

    if (!response.ok) {
      if (response.status === 401) {
        // Session expired or invalid, trigger re-authentication
        window.location.href = '/login';
        throw new Error('Session expired');
      }
      
      const error = await response.json().catch(() => ({ detail: 'Network error' }));
      throw new Error(error.detail || `HTTP error! status: ${response.status}`);
    }

    // Handle empty responses
    const text = await response.text();
    return text ? JSON.parse(text) : null;
  }

  // Health check
  async checkHealth() {
    const response = await fetch(`${API_BASE_URL}/api/healthz`, {
      credentials: 'include',
    });
    return response.ok;
  }

  // Auth endpoints
  async getCurrentUser() {
    return this.fetchWithSession('/api/auth/me');
  }

  async logout() {
    return this.fetchWithSession('/api/auth/logout', {
      method: 'POST',
    });
  }

  // Channel endpoints
  async getChannels() {
    return this.fetchWithSession('/api/channels');
  }

  async addChannel(channelData: any) {
    return this.fetchWithSession('/api/channels', {
      method: 'POST',
      body: JSON.stringify(channelData),
    });
  }

  async getChannelVideos(maxResults: number = 50) {
    return this.fetchWithSession(`/api/ab-tests/channel/videos?max_results=${maxResults}`);
  }

  async syncChannels() {
    return this.fetchWithSession('/api/channels/sync', {
      method: 'POST',
    });
  }

  // A/B Test endpoints
  async getABTests() {
    return this.fetchWithSession('/api/ab-tests');
  }

  async createABTest(testData: any) {
    return this.fetchWithSession('/api/ab-tests', {
      method: 'POST',
      body: JSON.stringify(testData),
    });
  }

  async updateABTest(testId: string, testData: any) {
    return this.fetchWithSession(`/api/ab-tests/${testId}`, {
      method: 'PUT',
      body: JSON.stringify(testData),
    });
  }

  async deleteABTest(testId: string) {
    return this.fetchWithSession(`/api/ab-tests/${testId}`, {
      method: 'DELETE',
    });
  }

  // Billing endpoints
  async getBillingStatus() {
    return this.fetchWithSession('/api/billing/status');
  }

  async createCheckoutSession(priceId: string) {
    return this.fetchWithSession('/api/billing/create-checkout-session', {
      method: 'POST',
      body: JSON.stringify({ price_id: priceId }),
    });
  }

  async cancelSubscription() {
    return this.fetchWithSession('/api/billing/cancel-subscription', {
      method: 'POST',
    });
  }

  async getUsageStats() {
    return this.fetchWithSession('/api/billing/usage');
  }
}

// Export singleton instance
export const apiClient = new ApiClient();