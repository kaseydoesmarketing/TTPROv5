import { createContext, useContext, useEffect, useState, useCallback } from 'react';
import { 
  signOut as firebaseSignOut, 
  onAuthStateChanged, 
  User as FirebaseUser
} from 'firebase/auth';
import { auth } from '../lib/firebase';
import { oauthConfigManager } from '../lib/oauth-config';
import { oauthHandler } from '../lib/oauth-handler';

interface User {
  uid: string;
  email: string;
  displayName: string | null;
  photoURL: string | null;
  emailVerified: boolean;
  accessToken?: string;
  refreshToken?: string;
  tokenExpirationTime?: number;
  getIdToken?: (forceRefresh?: boolean) => Promise<string>;
}

interface CustomAuthError {
  code: string;
  message: string;
  details?: string;
}

interface AuthContextType {
  currentUser: User | null;
  loading: boolean;
  authError: CustomAuthError | null;
  signInWithGoogle: () => Promise<void>;
  logout: () => Promise<void>;
  getAuthToken: (forceRefresh?: boolean) => Promise<string | null>;
  refreshAuthToken: () => Promise<string | null>;
  clearAuthError: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

interface AuthProviderProps {
  children: React.ReactNode;
}

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export function AuthProvider({ children }: AuthProviderProps) {
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [authError, setAuthError] = useState<CustomAuthError | null>(null);

  const clearAuthError = useCallback(() => {
    setAuthError(null);
  }, []);

  const handleAuthError = useCallback((error: unknown, context: string) => {
    let authError: CustomAuthError;

    if (error && typeof error === 'object' && 'code' in error) {
      switch ((error as { code: string }).code) {
        case 'auth/configuration-not-found':
        case 'auth/invalid-api-key':
          authError = {
            code: (error as { code: string }).code,
            message: 'Authentication configuration error. Please contact support.',
            details: 'Firebase configuration is invalid or missing'
          };
          break;
        case 'auth/network-request-failed':
          authError = {
            code: (error as { code: string }).code,
            message: 'Network error. Please check your internet connection and try again.',
            details: 'Unable to connect to authentication servers'
          };
          break;
        case 'auth/too-many-requests':
          authError = {
            code: (error as { code: string }).code,
            message: 'Too many failed attempts. Please try again later.',
            details: 'Rate limit exceeded for authentication requests'
          };
          break;
        case 'auth/user-disabled':
          authError = {
            code: (error as { code: string }).code,
            message: 'Your account has been disabled. Please contact support.',
            details: 'User account is disabled'
          };
          break;
        case 'auth/popup-blocked':
        case 'auth/popup-closed-by-user':
          authError = {
            code: (error as { code: string }).code,
            message: 'Sign-in was cancelled. Please try again.',
            details: 'Authentication popup was blocked or closed'
          };
          break;
        default:
          authError = {
            code: (error as { code: string }).code,
            message: 'Authentication failed. Please try again.',
            details: (error as { message?: string }).message || 'Unknown error'
          };
      }
    } else {
      authError = {
        code: 'unknown',
        message: `${context} failed. Please try again.`,
        details: (error && typeof error === 'object' && 'message' in error ? (error as { message: string }).message : null) || 'Unknown error occurred'
      };
    }

    setAuthError(authError);
    return authError;
  }, []);

  const createUserFromFirebaseUser = useCallback(async (firebaseUser: FirebaseUser, accessToken?: string): Promise<User> => {
    if (!firebaseUser.email) {
      throw new Error('User email is required');
    }

    const idTokenResult = await firebaseUser.getIdTokenResult();
    
    return {
      uid: firebaseUser.uid,
      email: firebaseUser.email,
      displayName: firebaseUser.displayName,
      photoURL: firebaseUser.photoURL,
      emailVerified: firebaseUser.emailVerified,
      accessToken: accessToken,
      refreshToken: firebaseUser.refreshToken,
      tokenExpirationTime: idTokenResult.expirationTime ? new Date(idTokenResult.expirationTime).getTime() : undefined,
      getIdToken: (forceRefresh?: boolean) => firebaseUser.getIdToken(forceRefresh)
    };
  }, []);

  const getAuthToken = useCallback(async (forceRefresh: boolean = false): Promise<string | null> => {
    if (!auth.currentUser) {
      return null;
    }

    try {
      const token = await auth.currentUser.getIdToken(forceRefresh);
      
      if (currentUser && forceRefresh) {
        const idTokenResult = await auth.currentUser.getIdTokenResult();
        setCurrentUser(prev => prev ? {
          ...prev,
          tokenExpirationTime: idTokenResult.expirationTime ? new Date(idTokenResult.expirationTime).getTime() : undefined
        } : null);
      }
      
      return token;
    } catch (error: unknown) {
      handleAuthError(error, 'Token refresh');
      return null;
    }
  }, [currentUser, handleAuthError]);

  const refreshAuthToken = useCallback(async (): Promise<string | null> => {
    return await getAuthToken(true);
  }, [getAuthToken]);

  const registerUserWithBackend = useCallback(async (user: User): Promise<void> => {
    try {
      const token = await getAuthToken();
      if (!token) {
        throw new Error('No authentication token available');
      }

      const response = await fetch(`${API_BASE_URL}/auth/register`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          access_token: user.accessToken,
          refresh_token: user.refreshToken
        })
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Registration failed with status ${response.status}`);
      }

    } catch (error: unknown) {
      handleAuthError(error, 'User registration');
      throw error;
    }
  }, [getAuthToken, handleAuthError]);

  const revokeUserTokens = useCallback(async (): Promise<void> => {
    try {
      const token = await getAuthToken();
      if (!token) return;

      await fetch(`${API_BASE_URL}/auth/revoke`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });
    } catch (error) {
      console.debug('Token revocation failed during logout:', error);
    }
  }, [getAuthToken]);

  const signInWithGoogle = useCallback(async () => {
    try {
      setLoading(true);
      setAuthError(null);
      
      console.log('🚀 Starting robust OAuth flow...');
      
      // Initialize OAuth configuration
      await oauthConfigManager.initializeConfig();
      oauthConfigManager.validateEnvironment();
      
      // Use robust OAuth handler
      const result = await oauthHandler.signInWithGoogle();
      
      if (!result.success) {
        throw new Error(result.error || 'OAuth flow failed');
      }
      
      console.log('✅ OAuth flow completed, creating user...');
      const user = await createUserFromFirebaseUser(auth.currentUser!, result.accessToken);
      setCurrentUser(user);
      
      console.log('✅ User authenticated successfully');
      
    } catch (error: unknown) {
      console.error('❌ Sign-in failed:', error);
      setLoading(false);
      const authError = handleAuthError(error, 'Google sign-in');
      throw authError;
    } finally {
      setLoading(false);
    }
  }, [handleAuthError, createUserFromFirebaseUser]);

  const logout = useCallback(async () => {
    try {
      setLoading(true);
      setAuthError(null);
      
      if (currentUser) {
        await revokeUserTokens();
      }
      
      await firebaseSignOut(auth);
      setCurrentUser(null);
      
    } catch (error: unknown) {
      const authError = handleAuthError(error, 'Sign out');
      throw authError;
    }finally {
      setLoading(false);
    }
  }, [currentUser, handleAuthError, revokeUserTokens]);


  useEffect(() => {
    if (import.meta.env.DEV && import.meta.env.VITE_FIREBASE_API_KEY?.startsWith('dev_')) {
      const mockUser: User = {
        uid: 'dev-user-123',
        email: 'dev@example.com',
        displayName: 'Development User',
        photoURL: 'https://via.placeholder.com/40',
        emailVerified: true,
        accessToken: 'dev-access-token',
        refreshToken: 'dev-refresh-token',
        tokenExpirationTime: Date.now() + 3600000,
        getIdToken: async () => 'dev-id-token'
      };
      setCurrentUser(mockUser);
      setLoading(false);
      return () => {};
    }

    const unsubscribe = onAuthStateChanged(auth, async (firebaseUser) => {
      try {
        if (firebaseUser && firebaseUser.email) {
          const user = await createUserFromFirebaseUser(firebaseUser);
          setCurrentUser(user);
        } else {
          setCurrentUser(null);
        }
      } catch (error: unknown) {
        handleAuthError(error, 'Authentication state change');
        setCurrentUser(null);
      } finally {
        setLoading(false);
      }
    });

    return unsubscribe;
  }, [createUserFromFirebaseUser, handleAuthError]);

  // Initialize OAuth configuration on app start
  useEffect(() => {
    const initializeOAuth = async () => {
      try {
        console.log('🔧 Initializing OAuth configuration...');
        await oauthConfigManager.initializeConfig();
        oauthConfigManager.validateEnvironment();
        console.log('✅ OAuth configuration initialized');
      } catch (error) {
        console.error('❌ OAuth initialization failed:', error);
        handleAuthError(error, 'OAuth initialization');
      }
    };

    initializeOAuth();
  }, [handleAuthError]);

  const value: AuthContextType = {
    currentUser,
    loading,
    authError,
    signInWithGoogle,
    logout,
    getAuthToken,
    refreshAuthToken,
    clearAuthError,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}
