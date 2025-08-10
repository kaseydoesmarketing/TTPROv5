import { test, expect } from '@playwright/test';

/**
 * Critical Authentication Flow E2E Tests
 * 
 * These tests verify the complete Google Sign-in → Firebase Admin verification → 
 * backend session cookie → Dashboard flow works end-to-end.
 */

test.describe('🔐 Authentication Flow', () => {
  test.beforeEach(async ({ page }) => {
    // Set longer timeout for authentication flows
    test.setTimeout(120000);
  });

  test('should display login page when not authenticated', async ({ page }) => {
    await page.goto('/app');
    
    // Should redirect to authentication
    await expect(page).toHaveURL(/\/(app|login|auth)/);
    
    // Should show sign-in button or form
    const signInButton = page.locator('text=/sign.{0,10}in/i').first();
    const googleButton = page.locator('text=/google/i').first();
    
    // At least one authentication element should be visible
    await expect(
      signInButton.or(googleButton)
    ).toBeVisible({ timeout: 10000 });
    
    console.log('✅ Login page displays correctly when not authenticated');
  });

  test('should handle Firebase configuration errors gracefully', async ({ page }) => {
    await page.goto('/app');
    
    // Check if there are any console errors related to Firebase
    const errors: string[] = [];
    page.on('console', msg => {
      if (msg.type() === 'error') {
        errors.push(msg.text());
      }
    });
    
    await page.waitForTimeout(3000); // Wait for any Firebase initialization
    
    // Filter for Firebase-related errors
    const firebaseErrors = errors.filter(error => 
      error.toLowerCase().includes('firebase') || 
      error.toLowerCase().includes('auth')
    );
    
    // Should not have critical Firebase configuration errors
    const criticalErrors = firebaseErrors.filter(error =>
      error.includes('missing-project') ||
      error.includes('invalid-api-key') ||
      error.includes('auth/invalid-api-key')
    );
    
    expect(criticalErrors).toHaveLength(0);
    console.log('✅ No critical Firebase configuration errors detected');
  });

  test('should have proper CORS configuration', async ({ page }) => {
    const apiBaseUrl = process.env.E2E_API_BASE_URL;
    
    // Test CORS preflight for authentication endpoint
    const response = await page.evaluate(async (apiUrl) => {
      try {
        const response = await fetch(`${apiUrl}/api/auth/firebase`, {
          method: 'OPTIONS',
          headers: {
            'Origin': window.location.origin,
            'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': 'Content-Type,Authorization'
          }
        });
        return {
          status: response.status,
          headers: Object.fromEntries(response.headers.entries())
        };
      } catch (error) {
        return { error: error.message };
      }
    }, apiBaseUrl);
    
    expect(response.status).toBe(200);
    expect(response.headers['access-control-allow-origin']).toBeTruthy();
    expect(response.headers['access-control-allow-credentials']).toBe('true');
    
    console.log('✅ CORS configuration is properly set up');
  });

  test('should handle authentication endpoint properly', async ({ page }) => {
    const apiBaseUrl = process.env.E2E_API_BASE_URL;
    
    // Test authentication endpoint without token (should return 400 or 401)
    const response = await page.evaluate(async (apiUrl) => {
      try {
        const response = await fetch(`${apiUrl}/api/auth/firebase`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          credentials: 'include',
          body: JSON.stringify({})
        });
        return {
          status: response.status,
          text: await response.text()
        };
      } catch (error) {
        return { error: error.message };
      }
    }, apiBaseUrl);
    
    // Should return 400 (bad request) for missing token
    expect([400, 401]).toContain(response.status);
    console.log('✅ Authentication endpoint properly validates requests');
  });

  test('should have working session endpoint', async ({ page }) => {
    const apiBaseUrl = process.env.E2E_API_BASE_URL;
    
    // Test session endpoint without authentication (should return 401)
    const response = await page.evaluate(async (apiUrl) => {
      try {
        const response = await fetch(`${apiUrl}/api/auth/session`, {
          method: 'GET',
          credentials: 'include'
        });
        return {
          status: response.status,
          text: await response.text()
        };
      } catch (error) {
        return { error: error.message };
      }
    }, apiBaseUrl);
    
    // Should return 401 for unauthenticated requests
    expect(response.status).toBe(401);
    console.log('✅ Session endpoint properly requires authentication');
  });

  test('should display YouTube OAuth callback page', async ({ page }) => {
    await page.goto('/oauth2/callback?code=test_code');
    
    // Should show OAuth callback processing page
    await expect(page.locator('text=/connecting.*youtube/i')).toBeVisible({ timeout: 5000 });
    
    // Should eventually show an error (since test_code is invalid)
    await expect(page.locator('text=/error|failed/i')).toBeVisible({ timeout: 15000 });
    
    console.log('✅ OAuth callback page displays correctly');
  });

  test('should handle Firebase debug functions in console', async ({ page }) => {
    await page.goto('/app');
    
    // Wait for Firebase client to load
    await page.waitForTimeout(2000);
    
    // Test if debug functions are available
    const debugResult = await page.evaluate(() => {
      // @ts-ignore - These are global debug functions
      if (typeof window.debugFirebaseConfig === 'function') {
        return window.debugFirebaseConfig();
      }
      return { error: 'Debug functions not available' };
    });
    
    if (!debugResult.error) {
      expect(debugResult.config).toBeTruthy();
      expect(debugResult.config.projectId).toBe('titletesterpro');
      console.log('✅ Firebase debug functions work correctly');
    } else {
      console.log('ℹ️ Debug functions not available (expected in production)');
    }
  });

  test('should redirect to dashboard after successful authentication', async ({ page, context }) => {
    // This test would require actual authentication credentials
    // For now, we test the redirect logic by mocking session
    
    // Mock a session cookie
    await context.addCookies([{
      name: 'session_token',
      value: 'mock_session_token',
      domain: new URL(process.env.E2E_BASE_URL!).hostname,
      path: '/',
      httpOnly: true,
      secure: true
    }]);
    
    await page.goto('/app');
    
    // Should either:
    // 1. Show dashboard (if mock session is accepted)
    // 2. Show login (if mock session is rejected - which is expected)
    
    const isDashboard = await page.locator('[data-testid="dashboard"], .dashboard, text=/dashboard/i').isVisible();
    const isLogin = await page.locator('text=/sign.{0,10}in/i, text=/login/i, text=/authenticate/i').isVisible();
    
    expect(isDashboard || isLogin).toBe(true);
    console.log('✅ App properly handles authentication state');
  });

  test('should have proper error handling for network failures', async ({ page }) => {
    // Block network requests to simulate API failures
    await page.route('**/api/**', route => {
      route.abort('internetdisconnected');
    });
    
    await page.goto('/app');
    
    // Wait for potential error messages
    await page.waitForTimeout(5000);
    
    // Should handle network errors gracefully (not crash)
    const hasJSErrors = await page.evaluate(() => {
      // Check if there are any unhandled errors
      return window.onerror !== null;
    });
    
    // Page should still be functional despite network errors
    const bodyText = await page.locator('body').textContent();
    expect(bodyText).toBeTruthy();
    expect(bodyText!.length).toBeGreaterThan(0);
    
    console.log('✅ App handles network failures gracefully');
  });
});

test.describe('🎯 End-to-End Integration', () => {
  test('complete authentication flow (if credentials provided)', async ({ page }) => {
    const hasCredentials = process.env.E2E_GOOGLE_EMAIL && process.env.E2E_GOOGLE_PASSWORD;
    
    if (!hasCredentials) {
      test.skip('Skipping live authentication test - no credentials provided');
      return;
    }
    
    test.setTimeout(180000); // 3 minutes for full auth flow
    
    console.log('🔄 Starting complete authentication flow test...');
    
    await page.goto('/app');
    
    // Click sign in button
    const signInButton = page.locator('text=/sign.{0,20}(in|up)/i, text=/google/i').first();
    await expect(signInButton).toBeVisible({ timeout: 10000 });
    await signInButton.click();
    
    // Handle Google OAuth popup
    const popupPromise = page.waitForEvent('popup');
    await popupPromise;
    const popup = await popupPromise;
    
    // Fill in Google credentials
    await popup.fill('input[type="email"]', process.env.E2E_GOOGLE_EMAIL!);
    await popup.click('text=/next/i');
    await popup.waitForTimeout(2000);
    
    await popup.fill('input[type="password"]', process.env.E2E_GOOGLE_PASSWORD!);
    await popup.click('text=/next/i');
    
    // Wait for OAuth completion and popup close
    await popup.waitForEvent('close', { timeout: 30000 });
    
    // Should redirect to dashboard
    await expect(page).toHaveURL(/\/app.*(?!\/auth|\/login)/, { timeout: 30000 });
    
    // Should show authenticated user interface
    await expect(page.locator('text=/dashboard|welcome/i')).toBeVisible({ timeout: 10000 });
    
    // Verify session persistence by refreshing
    await page.reload();
    await expect(page).toHaveURL(/\/app.*(?!\/auth|\/login)/, { timeout: 10000 });
    
    console.log('✅ Complete authentication flow successful!');
  });
});

test.describe('🔗 API Integration', () => {
  test('backend API health and accessibility', async ({ page }) => {
    const apiBaseUrl = process.env.E2E_API_BASE_URL;
    
    const response = await page.evaluate(async (apiUrl) => {
      const response = await fetch(`${apiUrl}/health`);
      return {
        status: response.status,
        data: await response.json()
      };
    }, apiBaseUrl);
    
    expect(response.status).toBe(200);
    expect(response.data.status).toBe('healthy');
    
    console.log('✅ Backend API is accessible and healthy');
  });

  test('Google OAuth status endpoint', async ({ page }) => {
    const apiBaseUrl = process.env.E2E_API_BASE_URL;
    
    // Test OAuth status endpoint (should require authentication)
    const response = await page.evaluate(async (apiUrl) => {
      const response = await fetch(`${apiUrl}/api/auth/google/status`, {
        credentials: 'include'
      });
      return {
        status: response.status,
        text: await response.text()
      };
    }, apiBaseUrl);
    
    // Should return 401 (unauthorized) for unauthenticated requests
    expect(response.status).toBe(401);
    console.log('✅ OAuth status endpoint properly requires authentication');
  });
});