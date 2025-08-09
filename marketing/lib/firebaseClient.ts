import { initializeApp, getApps } from 'firebase/app';
import { getAuth, GoogleAuthProvider, signInWithPopup, signOut } from 'firebase/auth';

function clean(v?: string) {
  // Trim and remove all internal whitespace/newlines to avoid %0A iframe errors
  return (v ?? '').trim().replace(/\s+/g, '');
}

const firebaseConfig = {
  apiKey: clean(process.env.NEXT_PUBLIC_FIREBASE_API_KEY),
  authDomain: clean(process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN), // critical!!!
  projectId: clean(process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID),
  appId: clean(process.env.NEXT_PUBLIC_FIREBASE_APP_ID),
  messagingSenderId: clean(process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID),
};

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
    
    // Step 3: Send to backend
    const apiUrl = "https://ttprov4-k58o.onrender.com/api/auth/firebase";
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
    const preview = value ? `${value.substring(0, 10)}...` : "undefined";
    console.log(`  ${key}: ${status} (${preview})`);
  });
  
  console.log("\nCritical Checks:");
  console.log(`  Project ID: ${firebaseConfig.projectId || "MISSING"}`);
  console.log(`  Auth Domain: ${firebaseConfig.authDomain || "MISSING"}`);
  console.log(`  API Key: ${firebaseConfig.apiKey ? "Present" : "MISSING"}`);
  
  const expectedProjectId = "titletesterpro";
  const projectMatch = firebaseConfig.projectId === expectedProjectId;
  console.log(`  Project Match: ${projectMatch ? "✅ MATCH" : "❌ MISMATCH"} (expected: ${expectedProjectId})`);
  
  return firebaseConfig;
};

// Make debugging function available globally in development
if (typeof window !== 'undefined') {
  (window as any).debugFirebaseConfig = debugFirebaseConfig;
  (window as any).signInAndVerify = signInAndVerify;
}