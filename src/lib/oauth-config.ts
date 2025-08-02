/**
 * OAuth Configuration and Error Handling
 * Prevents OAuth failures with comprehensive validation and fallbacks
 */

interface OAuthConfig {
  frontendDomain: string;
  backendDomain: string;
  googleClientId: string;
  redirectUris: string[];
  requiredScopes: string[];
}

class OAuthConfigManager {
  private static instance: OAuthConfigManager;
  private config: OAuthConfig | null = null;

  private constructor() {}

  public static getInstance(): OAuthConfigManager {
    if (!OAuthConfigManager.instance) {
      OAuthConfigManager.instance = new OAuthConfigManager();
    }
    return OAuthConfigManager.instance;
  }

  public async initializeConfig(): Promise<OAuthConfig> {
    if (this.config) {
      return this.config;
    }

    // Get backend configuration
    const backendDomain = import.meta.env.VITE_API_URL || 'https://backend-production-c23c.up.railway.app';
    const frontendDomain = window.location.origin;

    try {
      // Fetch Google Client ID from backend
      const response = await fetch(`${backendDomain}/auth/oauth/config`);
      if (!response.ok) {
        throw new Error(`Failed to fetch OAuth config: ${response.status}`);
      }
      
      const { google_client_id } = await response.json();
      
      this.config = {
        frontendDomain,
        backendDomain,
        googleClientId: google_client_id,
        redirectUris: [
          `${frontendDomain}/auth/callback`,
          `${backendDomain}/auth/oauth/callback`,
          `${frontendDomain}`,
          `${backendDomain}/auth/oauth/google/callback`
        ],
        requiredScopes: [
          'https://www.googleapis.com/auth/youtube',
          'https://www.googleapis.com/auth/youtube.readonly',
          'https://www.googleapis.com/auth/youtube.force-ssl',
          'profile',
          'email',
          'openid'
        ]
      };

      console.log('✅ OAuth Config initialized:', {
        frontendDomain: this.config.frontendDomain,
        backendDomain: this.config.backendDomain,
        clientId: this.config.googleClientId ? `${this.config.googleClientId.substring(0, 12)}...` : 'MISSING',
        redirectUris: this.config.redirectUris
      });

      return this.config;
    } catch (error) {
      console.error('❌ Failed to initialize OAuth config:', error);
      throw new Error(`OAuth configuration failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  public getConfig(): OAuthConfig {
    if (!this.config) {
      throw new Error('OAuth config not initialized. Call initializeConfig() first.');
    }
    return this.config;
  }

  public validateEnvironment(): void {
    const requiredEnvVars = [
      'VITE_API_URL',
      'VITE_FIREBASE_API_KEY',
      'VITE_FIREBASE_AUTH_DOMAIN',
      'VITE_FIREBASE_PROJECT_ID'
    ];

    const missingVars = requiredEnvVars.filter(varName => !import.meta.env[varName]);
    
    if (missingVars.length > 0) {
      throw new Error(`Missing required environment variables: ${missingVars.join(', ')}`);
    }

    console.log('✅ Environment variables validated');
  }

  public async validateGoogleOAuthSetup(): Promise<boolean> {
    try {
      const config = await this.initializeConfig();
      
      // Check if current domain is in allowed origins
      const currentDomain = window.location.origin;
      const isAllowedOrigin = config.redirectUris.some(uri => uri.startsWith(currentDomain));
      
      if (!isAllowedOrigin) {
        console.warn('⚠️ Current domain not in OAuth redirect URIs:', {
          currentDomain,
          allowedUris: config.redirectUris
        });
        return false;
      }

      // Test backend connectivity
      const backendResponse = await fetch(`${config.backendDomain}/health`);
      if (!backendResponse.ok) {
        console.warn('⚠️ Backend health check failed');
        return false;
      }

      console.log('✅ Google OAuth setup validated');
      return true;
    } catch (error) {
      console.error('❌ OAuth validation failed:', error);
      return false;
    }
  }
}

export const oauthConfigManager = OAuthConfigManager.getInstance();
export type { OAuthConfig };