import { chromium, FullConfig } from '@playwright/test';
import dotenv from 'dotenv';

async function globalSetup(config: FullConfig) {
  // Load environment variables
  dotenv.config();
  
  console.log('🚀 Starting global E2E test setup...');
  
  // Verify required environment variables
  const requiredEnvs = [
    'E2E_BASE_URL',
    'E2E_API_BASE_URL',
  ];
  
  const missingEnvs = requiredEnvs.filter(env => !process.env[env]);
  if (missingEnvs.length > 0) {
    console.error('❌ Missing required environment variables:', missingEnvs);
    console.error('Please copy .env.example to .env and configure the values');
    process.exit(1);
  }
  
  console.log('✅ Environment variables validated');
  console.log(`📍 Base URL: ${process.env.E2E_BASE_URL}`);
  console.log(`🔌 API URL: ${process.env.E2E_API_BASE_URL}`);
  
  // Health check on API backend
  try {
    const response = await fetch(`${process.env.E2E_API_BASE_URL}/health`);
    if (!response.ok) {
      throw new Error(`API health check failed: ${response.status}`);
    }
    const health = await response.json();
    console.log('✅ Backend API is healthy:', health);
  } catch (error) {
    console.error('❌ Backend API health check failed:', error);
    console.error('Please ensure the backend is running and accessible');
    process.exit(1);
  }
  
  // Test authentication setup if credentials provided
  if (process.env.E2E_GOOGLE_EMAIL && process.env.E2E_GOOGLE_PASSWORD) {
    console.log('🔐 Test authentication credentials detected');
    
    // Launch browser for auth setup
    const browser = await chromium.launch({ headless: true });
    const context = await browser.newContext();
    const page = await context.newPage();
    
    try {
      // Pre-authenticate and save session state
      console.log('🔄 Setting up authentication state...');
      
      await page.goto(`${process.env.E2E_BASE_URL}/app`);
      
      // Save the initial state for tests to use
      await context.storageState({ path: './auth-setup.json' });
      console.log('✅ Authentication setup completed');
      
    } catch (error) {
      console.warn('⚠️ Authentication setup failed (tests will handle auth manually):', error);
    } finally {
      await browser.close();
    }
  } else {
    console.log('ℹ️ No test credentials provided - tests will run without pre-authentication');
  }
  
  console.log('✅ Global setup completed successfully!');
}

export default globalSetup;