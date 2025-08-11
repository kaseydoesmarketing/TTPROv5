# Vercel Deployment Checklist

## Required Vercel Dashboard Configuration

### 1. Set Production Branch
**Path**: Project → Settings → Environments → Production → Branch Tracking  
**Action**: Set Production Branch = `bootstrap/v5`  
**Why**: This tells Vercel which branch to use for production deployments

### 2. Configure Root Directory  
**Path**: Project → Settings → Build & Development Settings → Root Directory  
**Action**: Set to `/marketing`  
**Why**: The Next.js app is in the marketing folder, not the repository root

### 3. Set Environment Variables
**Path**: Project → Settings → Environment Variables  
**Action**: Add the following:
- `NEXT_PUBLIC_API_BASE_URL` = `https://ttprov5.onrender.com`
- `NEXT_PUBLIC_FIREBASE_API_KEY` = (your Firebase API key)
- `NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN` = (your Firebase auth domain)
- `NEXT_PUBLIC_FIREBASE_PROJECT_ID` = (your Firebase project ID)

### 4. Configure Deploy Hooks (Optional)
**Path**: Project → Settings → Git → Deploy Hooks  
**Action**: Create a deploy hook with Branch = `bootstrap/v5`  
**Why**: Allows triggering deployments via webhook or admin panel

### 5. Trigger Initial Deployment
**Options**:
- Push a commit to `bootstrap/v5` branch
- OR from Deployments tab, find a recent commit and click "Redeploy"
- OR use the Deploy Hook URL if configured

## Verification Steps

After deployment, verify:

1. **Next.js Detection**: Check build logs for "Next.js detected"
2. **Environment Variables**: In build logs, confirm env vars are loaded
3. **Routes Work**: Test `/app`, `/app/channels`, `/app/tests` paths
4. **API Connection**: Check browser console for successful API calls to ttprov5.onrender.com

## Troubleshooting

- **"No Next.js version detected"**: Verify Root Directory is set to `/marketing`
- **Wrong branch deploying**: Check Production Branch setting
- **API calls failing**: Verify NEXT_PUBLIC_API_BASE_URL is set correctly
- **Firebase auth issues**: Check all Firebase env vars are set