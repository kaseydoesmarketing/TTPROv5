# Google Authentication Deployment Guide

## Overview
This guide covers the deployment requirements for the rebuilt Google Authentication system using Firebase Authentication and Google OAuth 2.0.

## Required Environment Variables

### Backend (.env)
```bash
# Database Configuration
DATABASE_URL=sqlite:///./app.db  # or your production database URL
REDIS_URL=redis://localhost:6379  # or your production Redis URL

# Firebase Admin SDK Configuration (Required for backend authentication)
FIREBASE_PROJECT_ID=your_firebase_project_id
FIREBASE_PRIVATE_KEY_ID=your_firebase_private_key_id
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nyour_firebase_private_key_content\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL=firebase-adminsdk-xxxxx@your_project_id.iam.gserviceaccount.com
FIREBASE_CLIENT_ID=your_firebase_client_id
FIREBASE_AUTH_URI=https://accounts.google.com/o/oauth2/auth
FIREBASE_TOKEN_URI=https://oauth2.googleapis.com/token
FIREBASE_AUTH_PROVIDER_X509_CERT_URL=https://www.googleapis.com/oauth2/v1/certs
FIREBASE_CLIENT_X509_CERT_URL=https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-xxxxx%40your_project_id.iam.gserviceaccount.com

# Google OAuth Configuration (Required for YouTube API access)
GOOGLE_CLIENT_ID=your_google_oauth_client_id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your_google_oauth_client_secret

# YouTube API Configuration (Required for video title management)
YOUTUBE_API_KEY=your_youtube_data_api_v3_key

# Application Configuration
SECRET_KEY=your_secure_secret_key_for_jwt_signing
CORS_ORIGINS=["http://localhost:3000","http://localhost:5173","https://ttprov4.vercel.app","https://titletesterpro.com"]

# Environment
ENVIRONMENT=production
LOG_LEVEL=INFO
```

### Frontend (.env)
```bash
# API Configuration
VITE_API_URL=https://your-backend-domain.com

# Firebase Client SDK Configuration (Required for frontend authentication)
VITE_FIREBASE_API_KEY=your_firebase_web_api_key
VITE_FIREBASE_AUTH_DOMAIN=your_project_id.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your_firebase_project_id
VITE_FIREBASE_DATABASE_URL=https://your_project_id-default-rtdb.firebaseio.com/
VITE_FIREBASE_STORAGE_BUCKET=your_project_id.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=your_firebase_messaging_sender_id
VITE_FIREBASE_APP_ID=1:your_sender_id:web:your_app_id
VITE_FIREBASE_MEASUREMENT_ID=G-your_measurement_id

# Environment
NODE_ENV=production
```

## Google Cloud Console Configuration

### 1. OAuth 2.0 Client Setup
- Navigate to Google Cloud Console > APIs & Services > Credentials
- Create or update OAuth 2.0 Client ID
- **Authorized JavaScript origins:**
  - `https://your-frontend-domain.com`
  - `https://ttprov4.vercel.app` (if using Vercel)
  - `https://titletesterpro.com` (production domain)
- **Authorized redirect URIs:**
  - `https://your-frontend-domain.com/__/auth/handler`
  - `https://ttprov4.vercel.app/__/auth/handler`
  - `https://titletesterpro.com/__/auth/handler`

### 2. Enable Required APIs
- Firebase Authentication API
- YouTube Data API v3
- Google Identity Toolkit API

## Firebase Console Configuration

### 1. Authentication Setup
- Enable Google Sign-in provider
- Add authorized domains:
  - `your-frontend-domain.com`
  - `ttprov4.vercel.app`
  - `titletesterpro.com`

### 2. Realtime Database Setup
- Enable Firebase Realtime Database
- Configure security rules for authenticated users

### 3. Service Account Key
- Generate a new private key for Firebase Admin SDK
- Use the downloaded JSON for backend environment variables

## Deployment Checklist

### Pre-deployment
- [ ] Firebase project created and configured
- [ ] Google OAuth client created with correct domains
- [ ] YouTube Data API enabled
- [ ] Service account key generated
- [ ] All environment variables configured in deployment platform

### Post-deployment
- [ ] Test Google sign-in flow in production
- [ ] Verify YouTube API integration works
- [ ] Test token refresh functionality
- [ ] Verify protected routes work correctly
- [ ] Test logout functionality

## Security Considerations

1. **Environment Variables**: Never commit real credentials to version control
2. **CORS Configuration**: Ensure CORS_ORIGINS only includes trusted domains
3. **Firebase Rules**: Configure database security rules appropriately
4. **OAuth Scopes**: Only request necessary YouTube API scopes
5. **Token Storage**: Tokens are encrypted in the database using application secret key

## Troubleshooting

### Common Issues
1. **Invalid API Key**: Ensure Firebase Web API key is correct and project is enabled
2. **OAuth Redirect Mismatch**: Verify authorized redirect URIs match exactly
3. **CORS Errors**: Check CORS_ORIGINS includes your frontend domain
4. **Token Refresh Failures**: Verify Google OAuth client supports offline access

### Debug Steps
1. Check browser console for Firebase errors
2. Verify backend logs for authentication failures
3. Test API endpoints with valid tokens
4. Confirm environment variables are loaded correctly

## Migration Notes

### Removed Components
- All mock authentication code
- Development-only Firebase configurations
- Legacy OAuth implementations
- Unused environment variables

### New Features
- OAuth 2.0 Authorization Code Flow with PKCE
- Encrypted token storage
- Comprehensive error handling
- Token lifecycle management
- Production-ready Firebase integration
