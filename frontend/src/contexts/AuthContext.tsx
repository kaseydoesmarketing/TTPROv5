import { createContext, useContext, useEffect, useState } from 'react';
import { auth } from '../lib/firebase';

interface User {
  uid: string;
  email: string | null;
  displayName: string | null;
  photoURL: string | null;
  getIdToken?: () => Promise<string>;
}

interface AuthContextType {
  currentUser: User | null;
  loading: boolean;
  signInWithGoogle: () => Promise<void>;
  logout: () => Promise<void>;
  getAuthToken: () => Promise<string | null>;
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

export function AuthProvider({ children }: AuthProviderProps) {
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  const signInWithGoogle = async () => {
    try {
      console.log("Development mode: Using mock authentication");
      
      const mockUser = {
        uid: 'dev-user-123',
        email: 'dev@example.com',
        displayName: 'Dev User',
        photoURL: 'https://via.placeholder.com/150',
        getIdToken: async () => 'mock-dev-token'
      };
      
      setCurrentUser(mockUser as User);
      await registerUserWithBackend(mockUser as User);
      return;
    } catch (error) {
      console.error('Error in mock sign in:', error);
      const mockUser = {
        uid: 'dev-user-123',
        email: 'dev@example.com',
        displayName: 'Dev User',
        photoURL: 'https://via.placeholder.com/150',
        getIdToken: async () => 'mock-dev-token'
      };
      setCurrentUser(mockUser as User);
    }
  };

  const logout = async () => {
    try {
      console.log("Mock logout");
      setCurrentUser(null);
    } catch (error) {
      console.error('Error signing out:', error);
      throw error;
    }
  };

  const getAuthToken = async (): Promise<string | null> => {
    if (!currentUser) return null;
    
    return 'mock-dev-token';
  };

  const registerUserWithBackend = async (_user: User) => {
    try {
      const token = 'mock-dev-token';
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      
      const response = await fetch(`${apiUrl}/auth/register`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });
      
      if (!response.ok) {
        throw new Error('Failed to register user with backend');
      }
      
      const data = await response.json();
      console.log('User registered with backend:', data);
    } catch (error) {
      console.error('Error registering user with backend:', error);
    }
  };

  useEffect(() => {
    const unsubscribe = auth.onAuthStateChanged((user) => {
      setCurrentUser(user);
      setLoading(false);
    });
    return unsubscribe;
  }, []);

  const value: AuthContextType = {
    currentUser,
    loading,
    signInWithGoogle,
    logout,
    getAuthToken,
  };

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
}
