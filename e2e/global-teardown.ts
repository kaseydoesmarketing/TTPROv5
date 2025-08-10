import { FullConfig } from '@playwright/test';

async function globalTeardown(config: FullConfig) {
  console.log('🧹 Running global teardown...');
  
  // Clean up any global resources
  // Remove auth setup file if it exists
  try {
    const fs = require('fs');
    if (fs.existsSync('./auth-setup.json')) {
      fs.unlinkSync('./auth-setup.json');
      console.log('🗑️ Cleaned up authentication setup file');
    }
  } catch (error) {
    console.warn('⚠️ Could not clean up auth file:', error);
  }
  
  console.log('✅ Global teardown completed');
}

export default globalTeardown;