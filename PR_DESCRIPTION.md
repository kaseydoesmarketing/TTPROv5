# Fix Vercel Deployment & Firebase Auth Handshake

## Summary

This PR fixes the Vercel deployment configuration for TTPROv5 and implements a robust Firebase authentication handshake with automatic token refresh and session cookie management.

## Changes

### 1. Vercel Configuration Cleanup
- **Removed** root `vercel.json` that pointed to wrong backend (ttprov4)
- **Cleaned** `marketing/vercel.json` to remove branch toggles and env vars (these belong in dashboard)
- **Fixed** OAuth callback to use correct backend URL (`ttprov5.onrender.com`)

### 2. Firebase Auth Handshake Implementation
- **Created** `marketing/lib/authHandshake.ts` with:
  - Lazy Firebase loading to avoid initialization issues
  - Automatic token refresh on 401 responses
  - Session cookie verification
  - Retry logic for failed auth attempts
- **Updated** `marketing/lib/api.ts` to use `authenticatedFetch` for all API calls
- **Updated** `marketing/components/AuthGate.tsx` to use new handshake utility

### 3. Documentation
- **Created** `deploy/vercel-root.md` - Documents frontend location
- **Created** `VERCEL_DEPLOYMENT_CHECKLIST.md` - Step-by-step Vercel configuration guide

## Validation Steps

### 1. Next.js Detection Verification
**File Path**: `/marketing/package.json` (line 21)
```json
"next": "^14.0.0"
```
**Build Script**: Line 7
```json
"build": "next build"
```
✅ Vercel will detect Next.js when Root Directory is set to `/marketing`

### 2. Backend Auth Endpoint Test
```bash
# Test Firebase auth endpoint (replace YOUR_TOKEN with valid Firebase ID token)
curl -X POST https://ttprov5.onrender.com/api/auth/firebase \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"idToken": "YOUR_TOKEN"}' \
  -c cookies.txt \
  -v

# Expected: 200 OK response with Set-Cookie header for session
```

### 3. Session Cookie Verification
```javascript
// Run in browser DevTools after authentication
fetch('https://ttprov5.onrender.com/api/campaigns', {
  credentials: 'include'
}).then(r => console.log('Status:', r.status))

// Expected: 200 (not 401) if session cookie is working
```

### 4. Legacy Domain Check
```bash
# Check for old domains - should return nothing
grep -r "app.titletesterpro.com" marketing/
grep -r "ttprov4-k58o.onrender.com" marketing/

# All references now point to:
# - https://www.titletesterpro.com/app (routes)
# - https://ttprov5.onrender.com (API)
```

## Required Vercel Dashboard Configuration

After merging, configure these settings in Vercel Dashboard:

### 1. Production Branch
**Path**: Project → Settings → Environments → Production → Branch Tracking  
**Set**: Production Branch = `bootstrap/v5`

### 2. Root Directory
**Path**: Project → Settings → Build & Development Settings → Root Directory  
**Set**: `/marketing`

### 3. Environment Variables
**Path**: Project → Settings → Environment Variables  
Add:
- `NEXT_PUBLIC_API_BASE_URL` = `https://ttprov5.onrender.com`
- `NEXT_PUBLIC_FIREBASE_API_KEY` = (your key)
- `NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN` = (your domain)
- `NEXT_PUBLIC_FIREBASE_PROJECT_ID` = (your project)

### 4. Deploy Hook (Optional)
**Path**: Project → Settings → Git → Deploy Hooks  
**Create**: Hook with Branch = `bootstrap/v5`

### 5. Trigger Deployment
Push to `bootstrap/v5` or use Redeploy button on desired commit

## Files Changed
- ❌ Deleted: `/vercel.json` (incorrect root config)
- ✏️ Modified: `/marketing/vercel.json` (removed env vars and branch config)
- ✏️ Modified: `/marketing/app/oauth2/callback/page.tsx` (fixed API URL)
- ✏️ Modified: `/marketing/lib/api.ts` (added authenticatedFetch)
- ✏️ Modified: `/marketing/components/AuthGate.tsx` (use auth handshake)
- ✅ Added: `/marketing/lib/authHandshake.ts` (robust auth utility)
- ✅ Added: `/deploy/vercel-root.md` (root directory docs)
- ✅ Added: `/VERCEL_DEPLOYMENT_CHECKLIST.md` (deployment guide)

## Testing
1. Deploy to Vercel with Root Directory = `/marketing`
2. Sign in with Google
3. Verify session cookie is set
4. Check API calls succeed with cookie auth
5. Test 401 retry logic by clearing cookies mid-session