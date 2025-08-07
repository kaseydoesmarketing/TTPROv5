# OAuth Setup Guide - Bulletproof Configuration

This guide ensures OAuth authentication never fails again by providing comprehensive setup instructions and troubleshooting steps.

## 🔧 Required Environment Variables

### Frontend (Vercel)
Set these in Vercel Dashboard → Project Settings → Environment Variables:

```env
VITE_API_URL=https://backend-production-c23c.up.railway.app
VITE_FIREBASE_API_KEY=AIzaSyBosbRgJxRTWJpSfIIEbDP8EmmRXY0FjF8
VITE_FIREBASE_AUTH_DOMAIN=titletesterpro.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=titletesterpro
VITE_FIREBASE_DATABASE_URL=https://titletesterpro-default-rtdb.firebaseio.com
VITE_FIREBASE_STORAGE_BUCKET=titletesterpro.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=618794070994
VITE_FIREBASE_APP_ID=1:618794070994:web:154fb461d986c434eece0b
VITE_FIREBASE_MEASUREMENT_ID=G-CP6NQXEEW6
NODE_ENV=production
```

### Backend (Railway)
Set these in Railway Dashboard → Project Variables:

```env
GOOGLE_CLIENT_ID=618794070994-0p4hlg4devshr6l6bkdh3c4l4oh34flp.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=[Your Google Client Secret]
FIREBASE_PROJECT_ID=titletesterpro
FIREBASE_PRIVATE_KEY=[Your Firebase Private Key]
FIREBASE_CLIENT_EMAIL=firebase-adminsdk-xyz@titletesterpro.iam.gserviceaccount.com
YOUTUBE_API_KEY=AIzaSyAuXPhkFHX5NG3B74bs-zuBG3xmCO1h1RQ
```

## 🌐 Google Cloud Console Setup

### 1. OAuth 2.0 Client Configuration
Navigate to: Google Cloud Console → APIs & Services → Credentials

**Authorized JavaScript Origins:**
```
https://www.titletesterpro.com
https://titletesterpro.com
https://ttprov4.vercel.app
https://ttpr-ov4-9p5z-git-main-ttpro-live.vercel.app
http://localhost:3000
http://localhost:5173
```

**Authorized Redirect URIs:**
```
https://www.titletesterpro.com/auth/callback
https://www.titletesterpro.com
https://titletesterpro.com/auth/callback
https://titletesterpro.com
https://backend-production-c23c.up.railway.app/auth/oauth/callback
https://backend-production-c23c.up.railway.app/auth/oauth/google/callback
https://ttprov4.vercel.app/auth/callback
https://ttprov4.vercel.app
http://localhost:3000/auth/callback
http://localhost:5173/auth/callback
```

### 2. Required APIs
Enable these APIs in Google Cloud Console:
- YouTube Data API v3
- Google+ API (for profile access)
- Identity and Access Management (IAM) API

### 3. OAuth Consent Screen
- Application name: TitleTesterPro
- Authorized domains: titletesterpro.com
- Scopes:
  - email
  - profile
  - openid
  - https://www.googleapis.com/auth/youtube
  - https://www.googleapis.com/auth/youtube.readonly
  - https://www.googleapis.com/auth/youtube.force-ssl

## 🔄 OAuth Flow Architecture

### 1. Hybrid Authentication Flow (Popup + Redirect)
```
User clicks login
→ Frontend validates environment
→ Try Firebase popup with Google OAuth
   ├─ SUCCESS: Get tokens → Register with backend → Done
   └─ FAIL (COOP/popup blocked): Automatic redirect fallback
      └─ User redirected to Google → Returns to app → Auth completed
```

### 2. COOP Protection & Fallbacks
- **Cross-Origin-Opener-Policy**: Headers set to `same-origin-allow-popups`
- **Popup blocked detection**: Automatic fallback to redirect
- **COOP error handling**: Seamless redirect authentication
- **Browser compatibility**: Works in all security configurations

### 3. Error Handling & Retries
- **Firebase timeout**: 30 seconds with 3 retries
- **Backend registration**: 3 retries with exponential backoff
- **Token refresh**: Automatic when needed
- **Popup blocked**: Automatic redirect fallback (no user intervention)
- **COOP errors**: Seamless redirect authentication

## 🛠️ Troubleshooting

### Common Issues & Solutions

#### 1. "Invalid Google ID token" (401 error)
**Cause**: Token validation failed on backend
**Solution**:
```bash
# Check backend logs for specific error
# Verify GOOGLE_CLIENT_ID matches frontend
# Ensure clock sync between services
```

#### 2. "OAuth callback timeout"
**Cause**: Popup blocked or slow response
**Solution**:
- Check popup blocker settings
- Verify redirect URIs are correct
- Clear browser cache and cookies

#### 3. "Configuration not found"
**Cause**: Missing environment variables
**Solution**:
```bash
# Verify all required env vars are set
# Check spelling and formatting
# Restart services after changes
```

#### 4. CORS errors during OAuth
**Cause**: Missing domain in allowed origins
**Solution**:
```bash
# Add domain to Google OAuth origins
# Update Railway CORS_ORIGINS
# Verify protocol (http vs https)
```

## 🔍 Validation Commands

### Test Environment Setup
```bash
# Test backend connectivity
curl https://backend-production-c23c.up.railway.app/health

# Test OAuth config endpoint
curl https://backend-production-c23c.up.railway.app/auth/oauth/config

# Test frontend environment
npm run build && npm run preview
```

### Debug OAuth Flow
1. Open browser dev tools → Console
2. Look for OAuth initialization logs:
   - "🔧 Initializing OAuth configuration..."
   - "✅ OAuth configuration initialized"
   - "🚀 Starting robust OAuth flow..."

## 🚀 Deployment Checklist

Before deploying:
- [ ] All environment variables set in Vercel
- [ ] All environment variables set in Railway  
- [ ] Google OAuth origins include all domains
- [ ] Google OAuth redirects include all URLs
- [ ] Required APIs enabled in Google Cloud
- [ ] Firebase configuration matches project
- [ ] Backend health check passes
- [ ] Frontend builds without errors

## 📞 Emergency Recovery

If OAuth completely fails:
1. Check environment validator in browser console
2. Verify Google Cloud Console settings
3. Test with incognito browser window
4. Clear all browser data for domain
5. Contact support with error logs

## 🔐 Security Notes

- Never commit secrets to Git
- Rotate tokens every 90 days
- Monitor OAuth usage in Google Console
- Use environment-specific configurations
- Keep Firebase rules restrictive

---

**Last Updated**: January 2025
**Version**: 2.0 (Bulletproof Edition)