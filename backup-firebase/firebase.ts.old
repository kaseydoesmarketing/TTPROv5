import { initializeApp, FirebaseApp } from 'firebase/app';
import { getAuth, GoogleAuthProvider, Auth } from 'firebase/auth';
import { getDatabase, Database } from 'firebase/database';

interface FirebaseConfig {
  apiKey: string;
  authDomain: string;
  projectId: string;
  databaseURL?: string;
  storageBucket?: string;
  messagingSenderId?: string;
  appId?: string;
  measurementId?: string;
}

class FirebaseService {
  private static instance: FirebaseService;
  private app: FirebaseApp | null = null;
  private authInstance: Auth | null = null;
  private databaseInstance: Database | null = null;
  private googleProviderInstance: GoogleAuthProvider | null = null;

  private constructor() {}

  public static getInstance(): FirebaseService {
    if (!FirebaseService.instance) {
      FirebaseService.instance = new FirebaseService();
    }
    return FirebaseService.instance;
  }

  private validateConfig(config: FirebaseConfig): void {
    const requiredFields = ['apiKey', 'authDomain', 'projectId'] as const;
    const missingFields = requiredFields.filter(field => !config[field]);
    
    if (missingFields.length > 0) {
      throw new Error(
        `Firebase configuration error: Missing required fields: ${missingFields.join(', ')}. ` +
        'Please check your environment variables.'
      );
    }

    if (!config.apiKey.startsWith('AIza') && !config.apiKey.includes('placeholder') && !config.apiKey.startsWith('dev_')) {
      throw new Error('Firebase configuration error: Invalid API key format');
    }

    if (!config.authDomain.includes('.firebaseapp.com')) {
      throw new Error('Firebase configuration error: Invalid auth domain format');
    }
  }

  private initializeFirebase(): FirebaseApp {
    if (this.app) {
      return this.app;
    }

    if (import.meta.env.DEV) {
      console.log('Initializing Firebase with environment variables:', {
        VITE_FIREBASE_API_KEY: import.meta.env.VITE_FIREBASE_API_KEY ? '***configured***' : 'MISSING',
        VITE_FIREBASE_AUTH_DOMAIN: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN || 'MISSING',
        VITE_FIREBASE_PROJECT_ID: import.meta.env.VITE_FIREBASE_PROJECT_ID || 'MISSING',
        VITE_FIREBASE_DATABASE_URL: import.meta.env.VITE_FIREBASE_DATABASE_URL || 'MISSING',
        VITE_FIREBASE_STORAGE_BUCKET: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET || 'MISSING',
        VITE_FIREBASE_MESSAGING_SENDER_ID: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID || 'MISSING',
        VITE_FIREBASE_APP_ID: import.meta.env.VITE_FIREBASE_APP_ID || 'MISSING',
        VITE_FIREBASE_MEASUREMENT_ID: import.meta.env.VITE_FIREBASE_MEASUREMENT_ID || 'MISSING'
      });
    }

    const firebaseConfig: FirebaseConfig = {
      apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
      authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
      projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
      databaseURL: import.meta.env.VITE_FIREBASE_DATABASE_URL,
      storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
      messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
      appId: import.meta.env.VITE_FIREBASE_APP_ID,
      measurementId: import.meta.env.VITE_FIREBASE_MEASUREMENT_ID,
    };

    console.log('Firebase config being used:', {
      apiKey: firebaseConfig.apiKey ? `${firebaseConfig.apiKey.substring(0, 10)}...` : 'MISSING',
      authDomain: firebaseConfig.authDomain,
      projectId: firebaseConfig.projectId,
      hasOtherFields: !!(firebaseConfig.databaseURL && firebaseConfig.appId)
    });

    try {
      this.validateConfig(firebaseConfig);
      this.app = initializeApp(firebaseConfig);
      return this.app;
    } catch (error) {
      console.error('Failed to initialize Firebase:', error);
      throw error;
    }
  }

  public getAuth(): Auth {
    if (!this.authInstance) {
      const app = this.initializeFirebase();
      this.authInstance = getAuth(app);
    }
    return this.authInstance;
  }

  public getDatabase(): Database {
    if (!this.databaseInstance) {
      const app = this.initializeFirebase();
      this.databaseInstance = getDatabase(app);
    }
    return this.databaseInstance;
  }

  public getGoogleProvider(): GoogleAuthProvider {
    if (!this.googleProviderInstance) {
      this.googleProviderInstance = new GoogleAuthProvider();
      
      this.googleProviderInstance.addScope('https://www.googleapis.com/auth/youtube');
      this.googleProviderInstance.addScope('https://www.googleapis.com/auth/youtube.readonly');
      this.googleProviderInstance.addScope('https://www.googleapis.com/auth/youtube.force-ssl');
      this.googleProviderInstance.addScope('profile');
      this.googleProviderInstance.addScope('email');
      this.googleProviderInstance.addScope('openid');

      this.googleProviderInstance.setCustomParameters({
        prompt: 'consent',
        access_type: 'offline',
        include_granted_scopes: 'true',
        response_type: 'code',
      });
    }
    return this.googleProviderInstance;
  }

  public getApp(): FirebaseApp {
    return this.initializeFirebase();
  }
}

const firebaseService = FirebaseService.getInstance();

export const auth = firebaseService.getAuth();
export const realtimeDB = firebaseService.getDatabase();
export const googleProvider = firebaseService.getGoogleProvider();
export const app = firebaseService.getApp();

export default app;
