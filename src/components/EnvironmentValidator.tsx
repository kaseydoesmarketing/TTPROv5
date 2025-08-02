/**
 * Environment Validator Component
 * Validates all required environment variables and OAuth setup
 */

import { useEffect, useState } from 'react';
import { oauthConfigManager } from '../lib/oauth-config';

interface ValidationResult {
  isValid: boolean;
  errors: string[];
  warnings: string[];
}

export function EnvironmentValidator({ children }: { children: React.ReactNode }) {
  const [validation, setValidation] = useState<ValidationResult | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const validateEnvironment = async () => {
      const errors: string[] = [];
      const warnings: string[] = [];

      try {
        // Validate environment variables
        oauthConfigManager.validateEnvironment();
        
        // Validate OAuth setup
        const isOAuthValid = await oauthConfigManager.validateGoogleOAuthSetup();
        if (!isOAuthValid) {
          warnings.push('OAuth configuration validation failed - some features may not work correctly');
        }

        console.log('✅ Environment validation completed');
        setValidation({
          isValid: errors.length === 0,
          errors,
          warnings
        });
      } catch (error) {
        console.error('❌ Environment validation failed:', error);
        errors.push(error instanceof Error ? error.message : 'Unknown environment validation error');
        setValidation({
          isValid: false,
          errors,
          warnings
        });
      } finally {
        setIsLoading(false);
      }
    };

    validateEnvironment();
  }, []);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Validating environment...</p>
        </div>
      </div>
    );
  }

  if (!validation?.isValid) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-red-50">
        <div className="max-w-md mx-auto p-6 bg-white rounded-lg shadow-lg">
          <div className="text-center mb-4">
            <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-3">
              <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </div>
            <h1 className="text-xl font-semibold text-gray-900">Configuration Error</h1>
          </div>
          
          <div className="space-y-3">
            {validation.errors.map((error, index) => (
              <div key={index} className="p-3 bg-red-50 border border-red-200 rounded text-sm text-red-700">
                {error}
              </div>
            ))}
          </div>
          
          <div className="mt-4 text-center">
            <p className="text-sm text-gray-600">
              Please check your environment variables and try again.
            </p>
          </div>
        </div>
      </div>
    );
  }

  if (validation.warnings.length > 0) {
    console.warn('⚠️ Environment warnings:', validation.warnings);
  }

  return <>{children}</>;
}

export default EnvironmentValidator;