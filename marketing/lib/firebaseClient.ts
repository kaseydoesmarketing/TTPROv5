import { initializeApp, getApps } from 'firebase/app';
import { getAuth, GoogleAuthProvider, signInWithPopup, signOut } from 'firebase/auth';

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

// Validate critical environment variables
let firebaseConfig: any;
try {
  firebaseConfig = {
    apiKey: validateEnvVar('NEXT_PUBLIC_FIREBASE_API_KEY', process.env.NEXT_PUBLIC_FIREBASE_API_KEY),
    authDomain: validateEnvVar('NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN', process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN),
    projectId: validateEnvVar('NEXT_PUBLIC_FIREBASE_PROJECT_ID', process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID),
    appId: clean(process.env.NEXT_PUBLIC_FIREBASE_APP_ID),
    messagingSenderId: clean(process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID),
  };
  
  // Validate project ID matches expected value
  const expectedProjectId = 'titletesterpro';
  if (firebaseConfig.projectId !== expectedProjectId) {
    console.error(`❌ Firebase project mismatch: got '${firebaseConfig.projectId}', expected '${expectedProjectId}'`);
    throw new Error(`Firebase project ID mismatch: expected '${expectedProjectId}', got '${firebaseConfig.projectId}'`);
  }
  
  console.log('✅ Firebase configuration validated successfully');
} catch (error) {
  console.error('❌ Firebase configuration validation failed:', error);
  // Use fallback minimal config for development
  firebaseConfig = {
    apiKey: 'missing-api-key',
    authDomain: 'missing.firebaseapp.com',
    projectId: 'missing-project',
    appId: 'missing-app-id',
    messagingSenderId: '000000000000',
  };
  console.warn('⚠️ Using fallback Firebase configuration - authentication will fail');
}

const app = getApps().length ? getApps()[0] : initializeApp(firebaseConfig);
export const auth = getAuth(app);
export const googleProvider = new GoogleAuthProvider();

// Configure Google provider with YouTube scope
googleProvider.addScope('https://www.googleapis.com/auth/youtube.readonly');

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
    const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'https://ttprov4-k58o.onrender.com';
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
    
    return responseData;
    
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
  
  console.log(`  API Base URL: ${process.env.NEXT_PUBLIC_API_BASE_URL || 'Using default: https://ttprov4-k58o.onrender.com'}`);
  
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

// Make debugging function available globally in development
if (typeof window !== 'undefined') {
  (window as any).debugFirebaseConfig = debugFirebaseConfig;
  (window as any).signInAndVerify = signInAndVerify;
}