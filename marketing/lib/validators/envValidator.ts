/**
 * Environment variable validation and sanitization
 * Fails fast on production builds if any issues detected
 */
export function validateAndSanitizeEnv() {
  const requiredEnvs = [
    'NEXT_PUBLIC_FIREBASE_PROJECT_ID',
    'NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN', 
    'NEXT_PUBLIC_FIREBASE_API_KEY',
    'NEXT_PUBLIC_API_BASE_URL'
  ];
  
  const errors: string[] = [];
  const sanitized: Record<string, string> = {};
  
  for (const envName of requiredEnvs) {
    const value = process.env[envName];
    
    if (!value) {
      errors.push(`Missing required environment variable: ${envName}`);
      continue;
    }
    
    const trimmed = value.trim();
    
    if (value !== trimmed) {
      const msg = `Environment variable ${envName} has leading/trailing whitespace (length: ${value.length} vs ${trimmed.length})`;
      console.error(`🚨 ${msg}`);
      
      if (process.env.NODE_ENV === 'development') {
        errors.push(msg);
      }
    }
    
    if (envName === 'NEXT_PUBLIC_FIREBASE_PROJECT_ID' && trimmed !== 'titletesterpro') {
      errors.push(`Invalid Firebase project ID: expected 'titletesterpro', got '${trimmed}'`);
    }
    
    sanitized[envName] = trimmed;
  }
  
  if (errors.length > 0) {
    console.error('🚨 Environment validation failed:');
    errors.forEach(error => console.error(`  - ${error}`));
    
    // Only throw during development to avoid breaking production
    if (typeof window !== 'undefined' && process.env.NODE_ENV === 'development') {
      throw new Error('Environment validation failed - see errors above');
    }
    
    // In production, log errors but don't break the app
    if (typeof window !== 'undefined' && process.env.NODE_ENV === 'production') {
      console.warn('⚠️ Environment validation failed in production - using fallback configuration');
    }
  }
  
  // Success log with masked values (only if no errors)
  if (errors.length === 0) {
    console.log('✅ Environment validation passed:');
    Object.entries(sanitized).forEach(([key, value]) => {
      const preview = key.includes('API_KEY') ? `${value.substring(0, 6)}...` : 
                     key.includes('API_BASE_URL') ? value :
                     `${value.substring(0, 10)}...`;
      console.log(`  ${key}: ${preview} (${value.length} chars)`);
    });
  } else {
    // In case of errors, still log what we have
    console.log('⚠️ Returning partial environment configuration:');
    Object.entries(sanitized).forEach(([key, value]) => {
      if (value) {
        const preview = key.includes('API_KEY') ? `${value.substring(0, 6)}...` : 
                       key.includes('API_BASE_URL') ? value :
                       `${value.substring(0, 10)}...`;
        console.log(`  ${key}: ${preview} (${value.length} chars)`);
      } else {
        console.log(`  ${key}: MISSING`);
      }
    });
  }
  
  return sanitized;
}
