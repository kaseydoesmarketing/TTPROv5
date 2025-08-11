// marketing/lib/firebaseClient.ts
import { initializeApp, getApps, getApp } from 'firebase/app';
import {
  getAuth,
  GoogleAuthProvider,
  signInWithPopup,
  signOut,
} from 'firebase/auth';

const firebaseConfig = {
  apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY!,
  authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN!,
  projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID!,
  appId: process.env.NEXT_PUBLIC_FIREBASE_APP_ID, // optional
  messagingSenderId: process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID, // optional
};

if (!firebaseConfig.apiKey) {
  // Not secret; logging helps diagnose "missing-api-key"
  console.error('🔥 Firebase envs missing in client bundle:', {
    apiKey: (process.env.NEXT_PUBLIC_FIREBASE_API_KEY || '').slice(0, 6) + '…',
    authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN,
    projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID,
  });
}

const app = getApps().length ? getApp() : initializeApp(firebaseConfig);
const auth = getAuth(app);
const googleProvider = new GoogleAuthProvider();

// If you need YouTube scopes, uncomment:
// googleProvider.addScope('https://www.googleapis.com/auth/youtube.readonly');
// googleProvider.addScope('https://www.googleapis.com/auth/youtube');
// googleProvider.setCustomParameters({ prompt: 'consent', access_type: 'offline' });

export { auth, googleProvider };

export const signInWithGoogle = async () => {
  return signInWithPopup(auth, googleProvider);
};

export const signOutUser = async () => {
  await signOut(auth);
};

export const logout = async () => {
  await signOut(auth);
};