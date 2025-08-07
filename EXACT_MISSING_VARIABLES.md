# EXACT MISSING ENVIRONMENT VARIABLES

## RAILWAY WEB SERVICE - MISSING VARIABLES

**Current**: 9/16 configured
**Missing**: 7 critical variables

### Missing Variables (add these exact names):

```env
FIREBASE_PRIVATE_KEY_ID=your_new_key_id_here
FIREBASE_PRIVATE_KEY=-----BEGIN PRIVATE KEY-----\nyour_new_private_key_here\n-----END PRIVATE KEY-----
FIREBASE_CLIENT_EMAIL=your_new_client_email_here
FIREBASE_CLIENT_ID=your_new_client_id_here
GOOGLE_CLIENT_ID=your_google_oauth_client_id
GOOGLE_CLIENT_SECRET=your_google_oauth_secret
YOUTUBE_API_KEY=your_youtube_api_key
```

### Already Configured (don't change):
- `DATABASE_URL`
- `REDIS_URL` 
- `FIREBASE_PROJECT_ID`
- `FIREBASE_AUTH_URI`
- `FIREBASE_TOKEN_URI`
- `FIREBASE_AUTH_PROVIDER_X509_CERT_URL`
- `SECRET_KEY`
- `CORS_ORIGINS`
- `ENVIRONMENT`

## VERCEL FRONTEND - ALL MISSING

**Current**: 0/7 configured  
**Missing**: ALL environment variables

### Add ALL these to Vercel:

```env
VITE_API_URL=https://web-production-98a4c.up.railway.app
VITE_FIREBASE_API_KEY=same_value_as_YOUTUBE_API_KEY_above
VITE_FIREBASE_AUTH_DOMAIN=titletesterpro.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=titletesterpro
VITE_FIREBASE_STORAGE_BUCKET=titletesterpro.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=your_firebase_sender_id
VITE_FIREBASE_APP_ID=your_firebase_app_id
```

## STEP-BY-STEP ORDER

### 1. Railway First
1. Go to Railway → Web Service → Variables
2. Add the 7 missing variables above
3. Wait for automatic redeploy (3-5 minutes)

### 2. Vercel Second  
1. Go to Vercel → Project → Settings → Environment Variables
2. Add all 7 variables above
3. Trigger manual redeploy

### 3. Test
```bash
curl https://web-production-98a4c.up.railway.app/health
```
Must return: `"status": "operational"`

## CRITICAL NOTES

- **FIREBASE_PRIVATE_KEY**: Must have literal `\n` characters (not actual newlines)
- **All variables**: No quotes around values in Railway
- **Firebase values**: Must be from your NEW service account (old ones revoked)
- **VITE_FIREBASE_API_KEY**: Use same value as YOUTUBE_API_KEY