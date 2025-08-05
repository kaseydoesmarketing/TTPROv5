# EMERGENCY FIX: Complete Railway Environment Variables

## BACKEND EMERGENCY STATUS
```json
{
  "status": "emergency",
  "vars_configured": "9/16", 
  "missing_critical": 3,
  "can_start": false
}
```

## IMMEDIATE RAILWAY FIXES

### 1. Go to Railway Web Service Environment Variables
**URL**: https://railway.com/project/a4ed9479-2265-4e71-8378-1725357872f4

### 2. Add ALL Missing Variables to Web Service

Click **Variables** → **Raw Editor** → Paste ALL:

```env
DATABASE_URL=${{Postgres.DATABASE_URL}}
REDIS_URL=${{Redis.REDIS_URL}}
FIREBASE_PROJECT_ID=titletesterpro
FIREBASE_PRIVATE_KEY_ID=YOUR_NEW_KEY_ID
FIREBASE_PRIVATE_KEY=-----BEGIN PRIVATE KEY-----\nYOUR_NEW_PRIVATE_KEY\n-----END PRIVATE KEY-----
FIREBASE_CLIENT_EMAIL=YOUR_NEW_EMAIL
FIREBASE_CLIENT_ID=YOUR_NEW_CLIENT_ID
FIREBASE_AUTH_URI=https://accounts.google.com/o/oauth2/auth
FIREBASE_TOKEN_URI=https://oauth2.googleapis.com/token
FIREBASE_AUTH_PROVIDER_X509_CERT_URL=https://www.googleapis.com/oauth2/v1/certs
GOOGLE_CLIENT_ID=YOUR_GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET=YOUR_GOOGLE_CLIENT_SECRET
YOUTUBE_API_KEY=YOUR_YOUTUBE_API_KEY
SECRET_KEY=your-super-secret-key-for-jwt-signing-and-encryption
ENVIRONMENT=production
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,http://localhost:5174,https://ttprov4.vercel.app,https://titletesterpro.com
```

**CRITICAL**: Replace all YOUR_* placeholders with actual values from new Firebase service account.

### 3. Vercel Environment Variables

Go to Vercel project → Settings → Environment Variables:

```env
VITE_API_URL=https://web-production-98a4c.up.railway.app
VITE_FIREBASE_API_KEY=SAME_AS_YOUTUBE_API_KEY
VITE_FIREBASE_AUTH_DOMAIN=titletesterpro.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=titletesterpro
VITE_FIREBASE_STORAGE_BUCKET=titletesterpro.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=YOUR_FIREBASE_SENDER_ID
VITE_FIREBASE_APP_ID=YOUR_FIREBASE_APP_ID
```

### 4. Deploy Order
1. **Fix Railway variables first**
2. **Wait for Railway deployment**
3. **Then fix Vercel variables**
4. **Redeploy Vercel**

### 5. Success Check
```bash
curl https://web-production-98a4c.up.railway.app/health
```
Must return: `"status": "operational"`

## THIS MUST BE DONE NOW - NO MORE DELAYS