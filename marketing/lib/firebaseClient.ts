import { initializeApp, getApps } from 'firebase/app';
import { getAuth, GoogleAuthProvider, signInWithPopup, signOut } from 'firebase/auth';
import { validateAndSanitizeEnv } from './validators/envValidator';

function clean(v?: string) {
  // Trim and remove all internal whitespace/newlines to avoid %0A iframe errors
  return (v ?? '').trim().replace(/\s+/g, '');
}

function validateEnvVar(name: string, value?: string): string {
  if (!value || value.trim() === '') {
    throw new Error(`Missing required environment variable: ${name}`);
  }
  return clean(value);
}

// Initialize Firebase only on client side
let firebaseConfig: any;
let app: any;
let auth: any;
let googleProvider: any;

if (typeof window !== 'undefined') {
  // Client-side initialization
  let sanitizedEnv;
  
  try {
    sanitizedEnv = validateAndSanitizeEnv();
    console.log('✅ Environment validation passed');
  } catch (error) {
    console.error('❌ Environment validation failed:', error);
    // Fallback to direct environment access
    sanitizedEnv = {
      NEXT_PUBLIC_FIREBASE_API_KEY: process.env.NEXT_PUBLIC_FIREBASE_API_KEY,
      NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN,
      NEXT_PUBLIC_FIREBASE_PROJECT_ID: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID,
      NEXT_PUBLIC_API_BASE_URL: process.env.NEXT_PUBLIC_API_BASE_URL,
    };
    console.warn('⚠️ Using direct environment access as fallback');
  }

  // Always try to create a working Firebase config
  firebaseConfig = {
    apiKey: sanitizedEnv.NEXT_PUBLIC_FIREBASE_API_KEY || 'missing-api-key',
    authDomain: sanitizedEnv.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN || 'missing.firebaseapp.com',
    projectId: sanitizedEnv.NEXT_PUBLIC_FIREBASE_PROJECT_ID || 'missing-project',
    appId: clean(process.env.NEXT_PUBLIC_FIREBASE_APP_ID) || 'missing-app-id',
    messagingSenderId: clean(process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID) || '000000000000',
  };
  
  console.log('🔥 Firebase configuration created:');
  console.log(`  Project ID: ${firebaseConfig.projectId}`);
  console.log(`  Auth Domain: ${firebaseConfig.authDomain}`);
  console.log(`  API Key: ${firebaseConfig.apiKey ? firebaseConfig.apiKey.substring(0, 10) + '...' : 'missing'}`);
  
  // Validate we have the minimum required values
  const hasRequiredFields = firebaseConfig.apiKey !== 'missing-api-key' && 
                           firebaseConfig.projectId !== 'missing-project' && 
                           firebaseConfig.authDomain !== 'missing.firebaseapp.com';
  
  if (!hasRequiredFields) {
    console.error('❌ Critical Firebase configuration missing - authentication will not work');
    console.error('Check that these environment variables are set:', {
      NEXT_PUBLIC_FIREBASE_API_KEY: !!process.env.NEXT_PUBLIC_FIREBASE_API_KEY,
      NEXT_PUBLIC_FIREBASE_PROJECT_ID: !!process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID,
      NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN: !!process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN,
    });
  } else {
    console.log('✅ Firebase configuration has required fields');
  }

  app = getApps().length ? getApps()[0] : initializeApp(firebaseConfig);
  auth = getAuth(app);
  googleProvider = new GoogleAuthProvider();
  
  // Configure Google provider with YouTube read + write scopes for A/B testing
  googleProvider.addScope('https://www.googleapis.com/auth/youtube.readonly');
  googleProvider.addScope('https://www.googleapis.com/auth/youtube');
  
  // Set custom parameters for OAuth code flow (needed for refresh token)
  googleProvider.setCustomParameters({
    prompt: 'consent',
    access_type: 'offline'
  });
} else {
  // Server-side fallback
  firebaseConfig = {
    apiKey: 'server-side-placeholder',
    authDomain: 'server-side-placeholder.firebaseapp.com',
    projectId: 'server-side-placeholder',
    appId: 'server-side-placeholder',
    messagingSenderId: '000000000000',
  };
}

export { auth, googleProvider };

export const signInWithGoogle = async () => {
  try {
    const result = await signInWithPopup(auth, googleProvider);
    return result.user;
  } catch (error) {
    console.error('Error signing in with Google:', error);
    throw error;
  }
};

export const logout = async () => {
  try {
    await signOut(auth);
  } catch (error) {
    console.error('Error signing out:', error);
    throw error;
  }
};

/**
 * Enhanced signInAndVerify with comprehensive debugging
 * Use this to test the complete authentication flow
 */
export const signInAndVerify = async () => {
  console.log("🔍 STARTING FIREBASE AUTHENTICATION");
  console.log("===================================");
  
  console.log("Auth instance:", auth ? "✅ Valid" : "❌ Invalid");
  console.log("Firebase config:", {
    apiKey: firebaseConfig.apiKey ? `${firebaseConfig.apiKey.substring(0, 10)}...` : "Missing",
    authDomain: firebaseConfig.authDomain || "Missing", 
    projectId: firebaseConfig.projectId || "Missing"
  });
  
  try {
    // Step 1: Google OAuth popup
    console.log("📱 Opening Google OAuth popup...");
    const result = await signInWithPopup(auth, googleProvider);
    console.log("✅ Google OAuth successful");
    console.log("User info:", {
      uid: result.user.uid,
      email: result.user.email,
      displayName: result.user.displayName
    });
    
    // Step 2: Get FRESH ID token (force refresh)
    console.log("🔄 Getting fresh ID token...");
    const idToken = await result.user.getIdToken(true); // force refresh = true
    console.log("✅ Fresh ID token obtained");
    console.log("Token preview:", `${idToken.substring(0, 50)}...`);
    
    // Step 3: Validate token format and payload
    try {
      const tokenPayload = JSON.parse(atob(idToken.split('.')[1]));
      console.log("🔍 Token validation:", {
        aud: tokenPayload.aud,
        iss: tokenPayload.iss,
        projectMatch: tokenPayload.aud === firebaseConfig.projectId,
        expectedProject: firebaseConfig.projectId
      });
      
      if (tokenPayload.aud !== firebaseConfig.projectId) {
        console.error(`❌ Token audience mismatch: token=${tokenPayload.aud}, config=${firebaseConfig.projectId}`);
        throw new Error('Token audience does not match Firebase project configuration');
      }
    } catch (tokenError) {
      console.warn("⚠️ Token validation failed:", tokenError);
    }
    
    // Step 4: Send to backend
    const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'https://ttprov5.onrender.com';
    const apiUrl = `${apiBaseUrl}/api/auth/firebase`;
    console.log(`📤 Sending to backend: ${apiUrl}`);
    
    const requestPayload = {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${idToken}`,
      },
      body: JSON.stringify({ idToken }),
      credentials: "include" as RequestCredentials,
    };
    
    console.log("Request details:", {
      url: apiUrl,
      method: requestPayload.method,
      headers: {
        "Content-Type": requestPayload.headers["Content-Type"],
        "Authorization": `Bearer ${idToken.substring(0, 20)}...`
      },
      bodyPreview: `{"idToken":"${idToken.substring(0, 20)}..."}`
    });
    
    const res = await fetch(apiUrl, requestPayload);
    
    console.log("📥 Backend response:", {
      status: res.status,
      statusText: res.statusText,
      ok: res.ok
    });
    
    const responseText = await res.text();
    console.log("Response body:", responseText);
    
    if (!res.ok) {
      console.error("❌ Authentication failed");
      throw new Error(`Auth failed (${res.status}): ${responseText}`);
    }
    
    const responseData = JSON.parse(responseText);
    console.log("✅ Authentication successful:", responseData);
    console.log("🍪 Session cookie should now be set by the backend");
    
    // Test if session is working by checking session status
    console.log("🔍 Testing session status...");
    try {
      const sessionResponse = await fetch(`${apiBaseUrl}/api/auth/session`, {
        method: "GET",
        credentials: "include"  // Include cookies
      });
      
      if (sessionResponse.ok) {
        const sessionData = await sessionResponse.json();
        console.log("✅ Session verification successful:", sessionData);
        return { ...responseData, sessionVerified: true, sessionData };
      } else {
        console.warn("⚠️ Session verification failed:", await sessionResponse.text());
        return { ...responseData, sessionVerified: false };
      }
    } catch (sessionError) {
      console.error("❌ Session verification error:", sessionError);
      return { ...responseData, sessionVerified: false };
    }
    
  } catch (error) {
    console.error("❌ Authentication error:", error);
    throw error;
  }
};

/**
 * Check Firebase configuration in browser console
 */
export const debugFirebaseConfig = () => {
  console.log("🔍 FIREBASE FRONTEND CONFIGURATION");
  console.log("=================================");
  
  console.log("Environment Variables Status:");
  Object.entries(firebaseConfig).forEach(([key, value]) => {
    const status = value ? "✅ SET" : "❌ MISSING";
    const preview = value && typeof value === 'string' ? `${value.substring(0, 10)}...` : "undefined";
    console.log(`  ${key}: ${status} (${preview})`);
  });
  
  console.log("\nCritical Checks:");
  console.log(`  Project ID: ${firebaseConfig.projectId || "MISSING"}`);
  console.log(`  Auth Domain: ${firebaseConfig.authDomain || "MISSING"}`);
  console.log(`  API Key: ${firebaseConfig.apiKey ? "Present" : "MISSING"}`);
  
  const expectedProjectId = "titletesterpro";
  const projectMatch = firebaseConfig.projectId === expectedProjectId;
  console.log(`  Project Match: ${projectMatch ? "✅ MATCH" : "❌ MISMATCH"} (expected: ${expectedProjectId})`);
  
  console.log(`  API Base URL: ${process.env.NEXT_PUBLIC_API_BASE_URL || 'Using default: https://ttprov5.onrender.com'}`);
  
  return {
    config: firebaseConfig,
    environment: {
      NEXT_PUBLIC_FIREBASE_API_KEY: process.env.NEXT_PUBLIC_FIREBASE_API_KEY,
      NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN,
      NEXT_PUBLIC_FIREBASE_PROJECT_ID: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID,
      NEXT_PUBLIC_API_BASE_URL: process.env.NEXT_PUBLIC_API_BASE_URL,
    },
    validation: {
      projectMatch,
      expectedProject: expectedProjectId,
      configValid: firebaseConfig.projectId !== 'missing-project'
    }
  };
};

/**
 * Check if user has active session
 */
export const checkSession = async () => {
  try {
    const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'https://ttprov5.onrender.com';
    const response = await fetch(`${apiBaseUrl}/api/auth/session`, {
      method: "GET",
      credentials: "include"
    });
    
    if (response.ok) {
      const data = await response.json();
      console.log("✅ Active session found:", data);
      return data;
    } else {
      console.log("ℹ️ No active session");
      return null;
    }
  } catch (error) {
    console.error("❌ Session check error:", error);
    return null;
  }
};

/**
 * Logout and clear session
 */
export const logoutSession = async () => {
  try {
    const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'https://ttprov5.onrender.com';
    const response = await fetch(`${apiBaseUrl}/api/auth/logout`, {
      method: "POST",
      credentials: "include"
    });
    
    if (response.ok) {
      console.log("✅ Logged out successfully");
      // Also sign out from Firebase
      await signOut(auth);
      return true;
    } else {
      console.error("❌ Logout failed");
      return false;
    }
  } catch (error) {
    console.error("❌ Logout error:", error);
    return false;
  }
};

// Make debugging function available globally in development
if (typeof window !== 'undefined') {
  (window as any).debugFirebaseConfig = debugFirebaseConfig;
  (window as any).signInAndVerify = signInAndVerify;
  (window as any).checkSession = checkSession;
  (window as any).logoutSession = logoutSession;
}