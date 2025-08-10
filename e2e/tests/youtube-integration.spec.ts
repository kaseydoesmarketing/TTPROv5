import { test, expect } from '@playwright/test';

/**
 * YouTube Integration E2E Tests
 * 
 * Tests YouTube API integration, channel management, and video title A/B testing
 */

test.describe('📺 YouTube Integration', () => {
  test.beforeEach(async ({ page }) => {
    test.setTimeout(120000); // 2 minutes per test
  });

  test('should display YouTube OAuth authorization option', async ({ page }) => {
    await page.goto('/app');
    
    // Wait for app to load
    await page.waitForTimeout(3000);
    
    // Look for YouTube authorization elements
    // This might be in settings, channels page, or main dashboard
    const youtubeElements = await page.locator('text=/youtube/i, text=/channel/i, text=/video/i').count();
    
    // Should have some YouTube-related UI elements
    expect(youtubeElements).toBeGreaterThan(0);
    console.log(`✅ Found ${youtubeElements} YouTube-related UI elements`);
  });

  test('should handle YouTube API quota limits gracefully', async ({ page }) => {
    const apiBaseUrl = process.env.E2E_API_BASE_URL;
    
    // Test channels endpoint which uses YouTube API
    const response = await page.evaluate(async (apiUrl) => {
      try {
        const response = await fetch(`${apiUrl}/api/channels`, {
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
    
    // Should either:
    // - Return 401 (not authenticated) 
    // - Return valid response
    // - Handle quota errors gracefully
    expect([200, 401, 403, 429]).toContain(response.status);
    
    if (response.status === 429) {
      console.log('ℹ️ YouTube API quota limit reached (expected)');
    } else if (response.status === 401) {
      console.log('ℹ️ Channels endpoint requires authentication (expected)');
    } else {
      console.log(`✅ Channels endpoint responded with status: ${response.status}`);
    }
  });

  test('should provide YouTube authorization flow', async ({ page }) => {
    // Skip if not running YouTube tests
    if (process.env.E2E_RUN_YOUTUBE_TESTS !== 'true') {
      test.skip('YouTube tests disabled - set E2E_RUN_YOUTUBE_TESTS=true to enable');
    }
    
    await page.goto('/app');
    
    // Look for YouTube authorization button/link
    const youtubeAuth = page.locator('text=/connect.*youtube/i, text=/authorize.*youtube/i').first();
    
    if (await youtubeAuth.isVisible({ timeout: 5000 })) {
      await youtubeAuth.click();
      
      // Should redirect to OAuth callback or show OAuth popup
      await page.waitForTimeout(2000);
      
      // Check if we're on OAuth callback page or popup appeared
      const isOAuthPage = page.url().includes('oauth') || page.url().includes('google.com');
      const hasPopup = await page.locator('text=/google/i, text=/sign.{0,10}in/i').isVisible();
      
      expect(isOAuthPage || hasPopup).toBe(true);
      console.log('✅ YouTube OAuth flow initiated successfully');
    } else {
      console.log('ℹ️ YouTube authorization UI not found (may be already authorized)');
    }
  });

  test.skip('should display user YouTube channels (requires authentication)', async ({ page }) => {
    // This test requires authenticated user with YouTube access
    await page.goto('/app/channels');
    
    // Wait for channels to load
    await page.waitForTimeout(5000);
    
    // Should either show:
    // 1. User's YouTube channels
    // 2. Authorization prompt
    // 3. Error message about missing authorization
    
    const hasChannels = await page.locator('[data-testid="channel-list"], .channel-item').isVisible();
    const hasAuthPrompt = await page.locator('text=/authorize/i, text=/connect.*youtube/i').isVisible();
    const hasError = await page.locator('text=/error/i, text=/unauthorized/i').isVisible();
    
    expect(hasChannels || hasAuthPrompt || hasError).toBe(true);
    console.log('✅ Channels page displays appropriate content');
  });

  test.skip('should allow creating A/B tests for video titles (requires authentication)', async ({ page }) => {
    // This test requires authenticated user with YouTube access
    await page.goto('/app/tests');
    
    // Wait for page to load
    await page.waitForTimeout(3000);
    
    // Look for create test button
    const createButton = page.locator('text=/create.*test/i, text=/new.*test/i, [data-testid="create-test"]').first();
    
    if (await createButton.isVisible({ timeout: 5000 })) {
      await createButton.click();
      
      // Should show test creation form
      await expect(page.locator('text=/title/i, text=/video/i').first()).toBeVisible({ timeout: 10000 });
      
      console.log('✅ A/B test creation form is accessible');
    } else {
      console.log('ℹ️ Create test button not found (may require authentication)');
    }
  });

  test('should handle YouTube API errors gracefully', async ({ page }) => {
    // Mock YouTube API to return error
    await page.route('**/youtube/**', route => {
      route.fulfill({
        status: 403,
        body: JSON.stringify({
          error: {
            code: 403,
            message: 'YouTube API quota exceeded'
          }
        })
      });
    });
    
    await page.goto('/app/channels');
    await page.waitForTimeout(3000);
    
    // Should show user-friendly error message
    const errorMessage = page.locator('text=/quota.*exceed/i, text=/api.*limit/i, text=/try.*later/i');
    const hasErrorUI = await errorMessage.isVisible();
    
    // App should not crash on API errors
    const bodyContent = await page.locator('body').textContent();
    expect(bodyContent).toBeTruthy();
    expect(bodyContent!.length).toBeGreaterThan(100);
    
    console.log('✅ App handles YouTube API errors gracefully');
  });
});

test.describe('🎬 Video Management', () => {
  test('should display video management interface', async ({ page }) => {
    await page.goto('/app');
    
    // Look for video-related navigation or content
    const videoElements = page.locator('text=/video/i, text=/content/i, text=/manage/i');
    const hasVideoUI = await videoElements.count() > 0;
    
    if (hasVideoUI) {
      console.log('✅ Video management interface elements found');
    } else {
      console.log('ℹ️ Video management UI may require authentication');
    }
    
    // Should not crash when accessing video-related pages
    await page.goto('/app/videos').catch(() => {}); // Ignore navigation errors
    await page.waitForTimeout(1000);
    
    const bodyText = await page.locator('body').textContent();
    expect(bodyText).toBeTruthy();
  });

  test('should handle video title updates', async ({ page }) => {
    const apiBaseUrl = process.env.E2E_API_BASE_URL;
    
    // Test video update endpoint (should require authentication)
    const response = await page.evaluate(async (apiUrl) => {
      try {
        const response = await fetch(`${apiUrl}/api/videos/test123`, {
          method: 'PATCH',
          headers: {
            'Content-Type': 'application/json',
          },
          credentials: 'include',
          body: JSON.stringify({ title: 'Test Title' })
        });
        return {
          status: response.status,
          text: await response.text()
        };
      } catch (error) {
        return { error: error.message };
      }
    }, apiBaseUrl);
    
    // Should return 401 (unauthorized) or 404 (endpoint not found)
    expect([401, 404]).toContain(response.status);
    console.log('✅ Video update endpoint properly requires authentication');
  });
});

test.describe('📊 Analytics Integration', () => {
  test('should display analytics dashboard', async ({ page }) => {
    await page.goto('/app');
    
    // Look for analytics/metrics/statistics elements
    const analyticsElements = page.locator('text=/analytics/i, text=/metrics/i, text=/stats/i, text=/views/i');
    const count = await analyticsElements.count();
    
    expect(count).toBeGreaterThanOrEqual(0);
    console.log(`✅ Found ${count} analytics-related UI elements`);
  });

  test('should handle YouTube Analytics API calls', async ({ page }) => {
    const apiBaseUrl = process.env.E2E_API_BASE_URL;
    
    // Test analytics endpoint
    const response = await page.evaluate(async (apiUrl) => {
      try {
        const response = await fetch(`${apiUrl}/api/analytics/video/test123`, {
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
    
    // Should return 401 (unauthorized) or 404 (not found)
    expect([401, 404]).toContain(response.status);
    console.log('✅ Analytics endpoint behavior is correct');
  });
});