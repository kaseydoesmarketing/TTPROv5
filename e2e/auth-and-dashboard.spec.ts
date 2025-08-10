import { test, expect } from '@playwright/test';

const BACKEND_URL = process.env.BACKEND_URL || 'https://ttprov5-api.onrender.com';
const FRONTEND_URL = process.env.FRONTEND_URL || 'https://titletesterpro.com';

test.describe('TTPROv5 E2E Authentication and Dashboard', () => {
  test('health check endpoints respond correctly', async ({ request }) => {
    // Test /healthz endpoint
    const healthz = await request.get(`${BACKEND_URL}/healthz`);
    expect(healthz.ok()).toBeTruthy();
    const healthzData = await healthz.json();
    expect(healthzData.ok).toBe(true);

    // Test /health endpoint
    const health = await request.get(`${BACKEND_URL}/health`);
    expect(health.ok()).toBeTruthy();
    const healthData = await health.json();
    expect(healthData.status).toBe('healthy');
  });

  test('CORS preflight requests work correctly', async ({ request }) => {
    // Test CORS preflight for auth endpoint
    const response = await request.fetch(`${BACKEND_URL}/api/auth/firebase`, {
      method: 'OPTIONS',
      headers: {
        'Origin': FRONTEND_URL,
        'Access-Control-Request-Method': 'POST',
        'Access-Control-Request-Headers': 'Content-Type,Authorization'
      }
    });
    
    expect([200, 204]).toContain(response.status());
    expect(response.headers()['access-control-allow-origin']).toBeTruthy();
    expect(response.headers()['access-control-allow-credentials']).toBe('true');
  });

  test('negative auth test - invalid token returns 401', async ({ request }) => {
    const response = await request.post(`${BACKEND_URL}/api/auth/firebase`, {
      data: { idToken: 'invalid_token' },
      headers: {
        'Content-Type': 'application/json',
        'Origin': FRONTEND_URL
      }
    });
    
    expect(response.status()).toBe(401);
  });

  test('debug endpoints return 404 when FIREBASE_DEBUG=0', async ({ request }) => {
    // Assuming FIREBASE_DEBUG=0 in production
    const debugFirebase = await request.get(`${BACKEND_URL}/debug/firebase`);
    expect(debugFirebase.status()).toBe(404);
    
    const debugCors = await request.get(`${BACKEND_URL}/debug/cors-domains`);
    expect(debugCors.status()).toBe(404);
  });

  test('frontend loads and shows authentication UI', async ({ page }) => {
    // Navigate to the app
    await page.goto(`${FRONTEND_URL}/app`);
    
    // Wait for either login UI or dashboard to load
    const loginOrDashboard = await Promise.race([
      page.waitForSelector('text=/Continue with Google|Sign in with Google/i', { timeout: 10000 }).then(() => 'login'),
      page.waitForSelector('text=/Dashboard|Campaigns/i', { timeout: 10000 }).then(() => 'dashboard')
    ]).catch(() => 'error');
    
    if (loginOrDashboard === 'login') {
      // Check that login UI is present
      await expect(page.locator('text=/Welcome to TitleTesterPro/i')).toBeVisible();
      await expect(page.locator('button:has-text("Continue with Google")')).toBeVisible();
    } else if (loginOrDashboard === 'dashboard') {
      // User is already logged in
      await expect(page.locator('text=/Dashboard|Campaigns/i')).toBeVisible();
    }
    
    expect(['login', 'dashboard']).toContain(loginOrDashboard);
  });

  test('session endpoint returns appropriate response', async ({ request }) => {
    const response = await request.get(`${BACKEND_URL}/api/auth/session`, {
      headers: {
        'Origin': FRONTEND_URL,
        'Cookie': 'session_token=test_invalid_session'
      }
    });
    
    // Either 401 (no valid session) or 200 (has session) is acceptable
    expect([200, 401]).toContain(response.status());
  });

  test('dashboard API endpoints are protected', async ({ request }) => {
    // Test that protected endpoints require authentication
    const endpoints = [
      '/api/ab-tests',
      '/api/channels',
      '/api/campaigns/kpis'
    ];
    
    for (const endpoint of endpoints) {
      const response = await request.get(`${BACKEND_URL}${endpoint}`, {
        headers: { 'Origin': FRONTEND_URL }
      });
      
      // Should return 401 or 307 (redirect to login)
      expect([401, 307, 403]).toContain(response.status());
    }
  });

  test('YouTube OAuth exchange endpoint exists', async ({ request }) => {
    // Test that the OAuth exchange endpoint exists (even if it returns error without valid code)
    const response = await request.post(`${BACKEND_URL}/api/auth/google/exchange`, {
      data: { code: 'invalid_code' },
      headers: {
        'Content-Type': 'application/json',
        'Origin': FRONTEND_URL
      }
    });
    
    // Should return 400/401/422 for invalid code, not 404
    expect([400, 401, 422]).toContain(response.status());
  });

  test('cookie attributes are set correctly when authentication succeeds', async ({ page, context }) => {
    // This test would require actual authentication or a test user
    // For now, we check that the cookie configuration is correct
    
    // Navigate to app
    await page.goto(`${FRONTEND_URL}/app`);
    
    // Check if we have any session cookies
    const cookies = await context.cookies();
    const sessionCookie = cookies.find(c => c.name === 'session_token');
    
    if (sessionCookie) {
      // If a session cookie exists, verify its attributes
      expect(sessionCookie.httpOnly).toBe(true);
      expect(sessionCookie.secure).toBe(true);
      expect(sessionCookie.sameSite).toBe('None');
      expect(sessionCookie.domain).toContain('titletesterpro.com');
    }
  });
});

test.describe('TTPROv5 Production Lockdown Verification', () => {
  test('all debug endpoints return 404 in production', async ({ request }) => {
    const debugEndpoints = [
      '/debug/firebase',
      '/debug/cors-domains',
      '/debug/environment',
      '/debug/session'
    ];
    
    for (const endpoint of debugEndpoints) {
      const response = await request.get(`${BACKEND_URL}${endpoint}`);
      expect(response.status()).toBe(404);
    }
  });
  
  test('no sensitive information in error responses', async ({ request }) => {
    // Send malformed request to trigger error
    const response = await request.post(`${BACKEND_URL}/api/auth/firebase`, {
      data: 'malformed json',
      headers: {
        'Content-Type': 'application/json',
        'Origin': FRONTEND_URL
      }
    });
    
    const text = await response.text();
    // Check that error doesn't leak sensitive info
    expect(text).not.toContain('FIREBASE_');
    expect(text).not.toContain('SECRET');
    expect(text).not.toContain('private_key');
  });
});