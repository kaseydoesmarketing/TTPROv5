import { createContext, useContext, useEffect, useState, useCallback } from 'react';
import { 
  signInWithRedirect, 
  getRedirectResult,
  signOut as firebaseSignOut, 
  onAuthStateChanged, 
  GoogleAuthProvider,
  User as FirebaseUser,
  AuthError
} from 'firebase/auth';
import { auth, googleProvider } from '../lib/firebase';

interface User {
  uid: string;
  email: string;
  displayName: string | null;
  photoURL: string | null;
  emailVerified: boolean;
  accessToken?: string;
  refreshToken?: string;
  tokenExpirationTime?: number;
}

interface AuthError {
  code: string;
  message: string;
  details?: string;
}

interface AuthContextType {
  currentUser: User | null;
  loading: boolean;
  authError: AuthError | null;
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
  const [authError, setAuthError] = useState<AuthError | null>(null);

  const clearAuthError = useCallback(() => {
    setAuthError(null);
  }, []);

  const handleAuthError = useCallback((error: any, context: string) => {
    let authError: AuthError;

    if (error?.code) {
      switch (error.code) {
        case 'auth/configuration-not-found':
        case 'auth/invalid-api-key':
          authError = {
            code: error.code,
            message: 'Authentication configuration error. Please contact support.',
            details: 'Firebase configuration is invalid or missing'
          };
          break;
        case 'auth/network-request-failed':
          authError = {
            code: error.code,
            message: 'Network error. Please check your internet connection and try again.',
            details: 'Unable to connect to authentication servers'
          };
          break;
        case 'auth/too-many-requests':
          authError = {
            code: error.code,
            message: 'Too many failed attempts. Please try again later.',
            details: 'Rate limit exceeded for authentication requests'
          };
          break;
        case 'auth/user-disabled':
          authError = {
            code: error.code,
            message: 'Your account has been disabled. Please contact support.',
            details: 'User account is disabled'
          };
          break;
        case 'auth/popup-blocked':
        case 'auth/popup-closed-by-user':
          authError = {
            code: error.code,
            message: 'Sign-in was cancelled. Please try again.',
            details: 'Authentication popup was blocked or closed'
          };
          break;
        default:
          authError = {
            code: error.code,
            message: 'Authentication failed. Please try again.',
            details: error.message
          };
      }
    } else {
      authError = {
        code: 'unknown',
        message: `${context} failed. Please try again.`,
        details: error?.message || 'Unknown error occurred'
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
      tokenExpirationTime: idTokenResult.expirationTime ? new Date(idTokenResult.expirationTime).getTime() : undefined
    };
  }, []);

  const signInWithGoogle = useCallback(async () => {
    try {
      setLoading(true);
      setAuthError(null);
      
      await signInWithRedirect(auth, googleProvider);
      
    } catch (error: any) {
      setLoading(false);
      const authError = handleAuthError(error, 'Google sign-in');
      throw authError;
    }
  }, [handleAuthError]);

  const logout = useCallback(async () => {
    try {
      setLoading(true);
      setAuthError(null);
      
      if (currentUser) {
        await revokeUserTokens(currentUser.uid);
      }
      
      await firebaseSignOut(auth);
      setCurrentUser(null);
      
    } catch (error: any) {
      const authError = handleAuthError(error, 'Sign out');
      throw authError;
    } finally {
      setLoading(false);
    }
  }, [currentUser, handleAuthError]);

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
    } catch (error: any) {
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

    } catch (error: any) {
      handleAuthError(error, 'User registration');
      throw error;
    }
  }, [getAuthToken, handleAuthError]);

  const revokeUserTokens = useCallback(async (uid: string): Promise<void> => {
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
    }
  }, [getAuthToken]);

  useEffect(() => {
    const handleRedirectResult = async () => {
      try {
        const result = await getRedirectResult(auth);
        if (result) {
          const credential = GoogleAuthProvider.credentialFromResult(result);
          const accessToken = credential?.accessToken;
          
          const user = await createUserFromFirebaseUser(result.user, accessToken);
          setCurrentUser(user);
          
          await registerUserWithBackend(user);
        }
      } catch (error: any) {
        handleAuthError(error, 'Authentication redirect');
      } finally {
        setLoading(false);
      }
    };

    handleRedirectResult();
  }, [createUserFromFirebaseUser, registerUserWithBackend, handleAuthError]);

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (firebaseUser) => {
      try {
        if (firebaseUser && firebaseUser.email) {
          const user = await createUserFromFirebaseUser(firebaseUser);
          setCurrentUser(user);
        } else {
          setCurrentUser(null);
        }
      } catch (error: any) {
        handleAuthError(error, 'Authentication state change');
        setCurrentUser(null);
      } finally {
        setLoading(false);
      }
    });

    return unsubscribe;
  }, [createUserFromFirebaseUser, handleAuthError]);

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
