/**
 * Robust OAuth Handler with Error Recovery
 * Prevents OAuth timeouts and handles all edge cases
 */

import { signInWithPopup, AuthError, UserCredential } from 'firebase/auth';
import { auth, googleProvider } from './firebase';
import { oauthConfigManager } from './oauth-config';

interface OAuthResult {
  success: boolean;
  user?: any;
  error?: string;
  accessToken?: string;
  refreshToken?: string;
}

interface BackendRegistrationData {
  firebase_uid: string;
  email: string;
  display_name: string;
  photo_url?: string;
  google_access_token: string;
  google_refresh_token?: string;
}

class OAuthHandler {
  private static instance: OAuthHandler;
  private isProcessing = false;
  private maxRetries = 3;
  private timeoutMs = 30000; // 30 seconds

  private constructor() {}

  public static getInstance(): OAuthHandler {
    if (!OAuthHandler.instance) {
      OAuthHandler.instance = new OAuthHandler();
    }
    return OAuthHandler.instance;
  }

  public async signInWithGoogle(): Promise<OAuthResult> {
    if (this.isProcessing) {
      return { success: false, error: 'OAuth process already in progress' };
    }

    this.isProcessing = true;
    console.log('🚀 Starting Google OAuth flow...');

    try {
      // Validate OAuth setup first
      const isValidSetup = await oauthConfigManager.validateGoogleOAuthSetup();
      if (!isValidSetup) {
        throw new Error('OAuth setup validation failed');
      }

      // Attempt Firebase popup login with timeout
      const firebaseResult = await this.attemptFirebaseLogin();
      if (!firebaseResult.success) {
        throw new Error(firebaseResult.error || 'Firebase login failed');
      }

      // Register with backend
      const backendResult = await this.registerWithBackend(firebaseResult);
      if (!backendResult.success) {
        throw new Error(backendResult.error || 'Backend registration failed');
      }

      console.log('✅ OAuth flow completed successfully');
      return {
        success: true,
        user: firebaseResult.user,
        accessToken: firebaseResult.accessToken,
        refreshToken: firebaseResult.refreshToken
      };

    } catch (error) {
      console.error('❌ OAuth flow failed:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown OAuth error'
      };
    } finally {
      this.isProcessing = false;
    }
  }

  private async attemptFirebaseLogin(): Promise<OAuthResult> {
    for (let attempt = 1; attempt <= this.maxRetries; attempt++) {
      console.log(`🔄 Firebase login attempt ${attempt}/${this.maxRetries}`);
      
      try {
        const result = await this.firebaseLoginWithTimeout();
        
        if (result.user && result.accessToken) {
          console.log('✅ Firebase login successful');
          return { success: true, ...result };
        } else {
          throw new Error('Invalid Firebase login result');
        }
      } catch (error) {
        console.warn(`⚠️ Firebase login attempt ${attempt} failed:`, error);
        
        if (attempt === this.maxRetries) {
          return {
            success: false,
            error: `Firebase login failed after ${this.maxRetries} attempts: ${error instanceof Error ? error.message : 'Unknown error'}`
          };
        }
        
        // Wait before retry
        await new Promise(resolve => setTimeout(resolve, 1000 * attempt));
      }
    }
    
    return { success: false, error: 'Max retries exceeded' };
  }

  private async firebaseLoginWithTimeout(): Promise<any> {
    return new Promise(async (resolve, reject) => {
      const timeout = setTimeout(() => {
        reject(new Error('Firebase login timeout'));
      }, this.timeoutMs);

      try {
        console.log('🔑 Attempting Firebase popup...');
        
        // Clear any existing auth state
        if (auth.currentUser) {
          console.log('🔄 Clearing existing auth state...');
          await auth.signOut();
        }

        const result: UserCredential = await signInWithPopup(auth, googleProvider);
        const user = result.user;
        
        // Get tokens
        const accessToken = await user.getIdToken();
        const refreshToken = user.refreshToken;

        // Get Google access token from credential
        const googleAccessToken = (result as any)._tokenResponse?.oauthAccessToken;
        const googleRefreshToken = (result as any)._tokenResponse?.oauthRefreshToken;

        clearTimeout(timeout);
        resolve({
          user: {
            uid: user.uid,
            email: user.email,
            displayName: user.displayName,
            photoURL: user.photoURL,
            emailVerified: user.emailVerified
          },
          accessToken,
          refreshToken,
          googleAccessToken,
          googleRefreshToken
        });
      } catch (error) {
        clearTimeout(timeout);
        reject(error);
      }
    });
  }

  private async registerWithBackend(firebaseResult: any): Promise<OAuthResult> {
    const config = oauthConfigManager.getConfig();
    
    for (let attempt = 1; attempt <= this.maxRetries; attempt++) {
      console.log(`🔄 Backend registration attempt ${attempt}/${this.maxRetries}`);
      
      try {
        const registrationData: BackendRegistrationData = {
          firebase_uid: firebaseResult.user.uid,
          email: firebaseResult.user.email,
          display_name: firebaseResult.user.displayName || firebaseResult.user.email,
          photo_url: firebaseResult.user.photoURL,
          google_access_token: firebaseResult.googleAccessToken,
          google_refresh_token: firebaseResult.googleRefreshToken
        };

        const response = await fetch(`${config.backendDomain}/auth/register`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${firebaseResult.accessToken}`
          },
          body: JSON.stringify(registrationData)
        });

        if (response.ok || response.status === 409) {
          // 409 = user already exists, which is fine
          console.log('✅ Backend registration successful');
          return { success: true };
        } else {
          const errorData = await response.json().catch(() => ({}));
          throw new Error(`Backend registration failed: ${response.status} - ${errorData.detail || 'Unknown error'}`);
        }
      } catch (error) {
        console.warn(`⚠️ Backend registration attempt ${attempt} failed:`, error);
        
        if (attempt === this.maxRetries) {
          return {
            success: false,
            error: `Backend registration failed after ${this.maxRetries} attempts: ${error instanceof Error ? error.message : 'Unknown error'}`
          };
        }
        
        // Wait before retry
        await new Promise(resolve => setTimeout(resolve, 2000 * attempt));
      }
    }
    
    return { success: false, error: 'Max retries exceeded' };
  }

  public async validateAndRefreshTokens(): Promise<boolean> {
    try {
      const currentUser = auth.currentUser;
      if (!currentUser) {
        return false;
      }

      // Force token refresh
      const token = await currentUser.getIdToken(true);
      console.log('✅ Token refreshed successfully');
      return true;
    } catch (error) {
      console.error('❌ Token refresh failed:', error);
      return false;
    }
  }
}

export const oauthHandler = OAuthHandler.getInstance();
export type { OAuthResult };