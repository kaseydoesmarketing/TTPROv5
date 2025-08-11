/**
 * Firebase Authentication Handshake Utility
 * Handles the complete auth flow with retry logic and session cookie management
 */

import type { User } from 'firebase/auth';

// Lazy load Firebase to avoid initialization issues
let firebaseModule: any = null;
let authModule: any = null;

const loadFirebase = async () => {
  if (!firebaseModule) {
    const [firebase, auth] = await Promise.all([
      import('firebase/app'),
      import('firebase/auth')
    ]);
    firebaseModule = firebase;
    authModule = auth;
  }
  return { firebaseModule, authModule };
};

interface HandshakeResult {
  success: boolean;
  user?: any;
  sessionVerified?: boolean;
  error?: string;
}

/**
 * Perform Firebase authentication handshake with backend
 * @param forceRefresh - Whether to force token refresh
 * @returns HandshakeResult with success status and user data
 */
export async function performAuthHandshake(forceRefresh = false): Promise<HandshakeResult> {
  try {
    // Load Firebase modules
    const { authModule } = await loadFirebase();
    const auth = authModule.getAuth();
    
    // Get current user
    const currentUser: User | null = auth.currentUser;
    if (!currentUser) {
      console.log('No authenticated user found');
      return { success: false, error: 'No authenticated user' };
    }

    // Get ID token with optional force refresh
    console.log('Getting Firebase ID token...');
    const idToken = await currentUser.getIdToken(forceRefresh);
    
    // Get API base URL
    const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'https://ttprov5.onrender.com';
    
    // Perform handshake with backend
    const response = await fetch(`${apiBaseUrl}/api/auth/firebase`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${idToken}`
      },
      body: JSON.stringify({ idToken }),
      credentials: 'include' // Critical for cookie-based sessions
    });

    if (!response.ok) {
      // If 401, try once more with refreshed token
      if (response.status === 401 && !forceRefresh) {
        console.log('Got 401, retrying with refreshed token...');
        return performAuthHandshake(true);
      }
      
      const errorText = await response.text();
      console.error('Auth handshake failed:', response.status, errorText);
      return { 
        success: false, 
        error: `Authentication failed (${response.status}): ${errorText}` 
      };
    }

    const data = await response.json();
    console.log('Auth handshake successful:', data);

    // Verify session is working
    const sessionVerified = await verifySession(apiBaseUrl);
    
    return {
      success: true,
      user: data.user,
      sessionVerified
    };
  } catch (error) {
    console.error('Auth handshake error:', error);
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error'
    };
  }
}

/**
 * Verify that the session cookie is working
 */
async function verifySession(apiBaseUrl: string): Promise<boolean> {
  try {
    const response = await fetch(`${apiBaseUrl}/api/auth/session`, {
      method: 'GET',
      credentials: 'include'
    });
    
    if (response.ok) {
      const data = await response.json();
      console.log('Session verified:', data);
      return true;
    }
    
    console.warn('Session verification failed:', response.status);
    return false;
  } catch (error) {
    console.error('Session verification error:', error);
    return false;
  }
}

/**
 * Ensure user is authenticated and has valid session
 * Call this at app initialization or after sign-in
 */
export async function ensureAuthenticated(): Promise<HandshakeResult> {
  const { authModule } = await loadFirebase();
  const auth = authModule.getAuth();
  
  return new Promise((resolve) => {
    const unsubscribe = authModule.onAuthStateChanged(auth, async (user: User | null) => {
      unsubscribe(); // Cleanup listener
      
      if (user) {
        // User is signed in, perform handshake
        const result = await performAuthHandshake();
        resolve(result);
      } else {
        // No user signed in
        resolve({ success: false, error: 'User not signed in' });
      }
    });
  });
}

/**
 * Make an authenticated API request with automatic token refresh
 */
export async function authenticatedFetch(
  url: string,
  options: RequestInit = {}
): Promise<Response> {
  const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'https://ttprov5.onrender.com';
  const fullUrl = url.startsWith('http') ? url : `${apiBaseUrl}${url}`;
  
  // Always include credentials for cookie-based auth
  const fetchOptions: RequestInit = {
    ...options,
    credentials: 'include'
  };
  
  // Make the request
  const response = await fetch(fullUrl, fetchOptions);
  
  // If 401, try to refresh auth and retry once
  if (response.status === 401) {
    console.log('Got 401, attempting to refresh authentication...');
    const handshakeResult = await performAuthHandshake(true);
    
    if (handshakeResult.success) {
      // Retry the request
      console.log('Retrying request after auth refresh...');
      return fetch(fullUrl, fetchOptions);
    }
  }
  
  return response;
}

export default {
  performAuthHandshake,
  ensureAuthenticated,
  authenticatedFetch
};