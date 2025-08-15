// src/lib/api-auth0.ts
const RAW_BASE = import.meta.env.VITE_API_BASE_URL;

if (!RAW_BASE) {
  throw new Error(
    '[env] VITE_API_BASE_URL is missing. Set it to your v5 API, e.g. https://ttprov5.onrender.com'
  );
}

const API_BASE_URL = (() => {
  let b = RAW_BASE.trim();
  if (b.startsWith('http://') && /onrender\.com/.test(b)) b = b.replace(/^http:\/\//, 'https://');
  return b.replace(/\/$/, '');
})();

export class ApiClient {
  private async fetchWithSession(url: string, options: RequestInit = {}) {
    const res = await fetch(`${API_BASE_URL}${url}`, {
      credentials: 'include',
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(options.headers || {}),
      },
    });
    if (!res.ok) {
      const text = await res.text().catch(() => '');
      throw new Error(`API ${url} ${res.status}: ${text}`);
    }
    return res;
  }

  loginWithIdToken = async (idToken: string) =>
    this.fetchWithSession(`/api/auth/login`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${idToken}` },
      body: JSON.stringify({ idToken }),
    });

  logout = async () => this.fetchWithSession(`/api/auth/logout`, { method: 'POST' });

  getSession = async () => (await this.fetchWithSession(`/api/auth/session`, { method: 'GET' })).json();
}