# Prompt for Devin: Railway Backend + Vercel Frontend Deployment

## Task: Complete Railway + Vercel Deployment Setup for TitleTesterPro

### Repository Access
- GitHub Repository: `https://github.com/kaseydoesmarketing/TTPROv4`
- Branch: `main` (work directly on main branch)
- You should already have access to this repository

### ⚠️ IMPORTANT: Delete Existing Deployments First

**Before starting, DELETE any existing deployments:**

1. **Railway**:
   - Log into Railway dashboard
   - Look for ANY existing TTPROv4 projects
   - Go to Settings → Danger → Delete Project
   - Delete ALL TTPROv4 projects to start completely fresh

2. **Vercel**:
   - Log into Vercel dashboard
   - Look for ANY existing TTPROv4 projects
   - Go to Settings → Advanced → Delete Project
   - Delete ALL TTPROv4 projects

3. **GitHub Webhooks**:
   - Go to: https://github.com/kaseydoesmarketing/TTPROv4/settings/hooks
   - DELETE any existing Railway or Vercel webhooks
   - We'll create fresh ones during setup

**Why delete everything?**
- Ensures clean webhook connections
- Prevents conflicting deployments
- Avoids environment variable conflicts
- Guarantees both services sync properly

### Primary Instructions Files

1. **Main Setup Guide**: 
   - Path in repo: `/RAILWAY_COMPLETE_REBUILD_GUIDE.md`
   - Direct link: https://github.com/kaseydoesmarketing/TTPROv4/blob/main/RAILWAY_COMPLETE_REBUILD_GUIDE.md
   - Contains complete Railway setup instructions

2. **Environment Variables Reference**:
   - Path in repo: `/.env.example`
   - Direct link: https://github.com/kaseydoesmarketing/TTPROv4/blob/main/.env.example
   - Shows all required environment variables

3. **This Instructions File**:
   - Path in repo: `/DEVIN_RAILWAY_REBUILD_PROMPT.md`
   - Direct link: https://github.com/kaseydoesmarketing/TTPROv4/blob/main/DEVIN_RAILWAY_REBUILD_PROMPT.md

### Your Specific Tasks

## PART 1: Railway Backend Setup

1. **Delete existing Railway project** (if any exists)
   - Look for any TTPROv4 project in Railway dashboard
   - Delete it completely to start fresh

2. **Create new Railway project**
   - Follow the guide exactly as written
   - Name it: "TTPROv4-Production"

3. **CRITICAL: Ensure webhook is created**
   - After connecting GitHub, verify webhook exists
   - Check: GitHub repo → Settings → Webhooks
   - Must see Railway webhook with green checkmark

4. **Add all three services**
   - PostgreSQL (auto-injects DATABASE_URL)
   - Redis (auto-injects REDIS_URL) 
   - Your app service

5. **Environment variables**
   - The guide lists ALL required variables
   - Copy them exactly as shown
   - Pay special attention to FIREBASE_PRIVATE_KEY formatting

6. **Get Railway backend URL**
   - After deployment, copy your Railway app URL
   - Example: `https://ttprov4-production-xxxx.railway.app`
   - You'll need this for Vercel

## PART 2: Vercel Frontend Setup

### CRITICAL: Frontend-Backend Synchronization

1. **Connect Vercel to same GitHub repo**
   - Import from: `kaseydoesmarketing/TTPROv4`
   - Root directory: Leave as is (monorepo structure)
   - Framework preset: Vite
   - Build command: `npm run build`
   - Output directory: `dist`

2. **Set Vercel Environment Variables**
   ```
   VITE_API_URL=https://your-railway-backend.railway.app
   VITE_FIREBASE_API_KEY=same-as-backend
   VITE_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
   VITE_FIREBASE_PROJECT_ID=same-as-backend
   VITE_FIREBASE_STORAGE_BUCKET=your-project.appspot.com
   VITE_FIREBASE_MESSAGING_SENDER_ID=from-firebase-console
   VITE_FIREBASE_APP_ID=from-firebase-console
   ```

3. **Update Railway CORS_ORIGINS**
   After Vercel deployment, go back to Railway and update:
   ```
   CORS_ORIGINS=https://your-app.vercel.app,https://your-custom-domain.com,http://localhost:5173,http://localhost:5174
   ```
   Include ALL domains where frontend will run

4. **Enable Auto-Deploy on Vercel**
   - Vercel Settings → Git
   - Enable "Auto-deploy on push to main"
   - Both Railway and Vercel will deploy on same git push

## PART 3: Synchronization Setup

### Ensure Both Deploy Together:
1. **Single Git Push = Both Deploy**
   - Railway backend auto-deploys on push to main
   - Vercel frontend auto-deploys on push to main
   - They stay in sync automatically

2. **Webhook Verification**
   Check GitHub → Settings → Webhooks:
   - Should see Railway webhook ✓
   - Should see Vercel webhook ✓
   - Both should show green checkmarks

3. **Environment Variable Sync**
   Critical variables that MUST match:
   - Firebase Project ID (backend & frontend)
   - API URL (frontend points to Railway backend)
   - CORS origins (backend allows Vercel frontend)

### Important Notes

- **Do NOT create a separate fork** - work on the main repository
- **Do NOT create feature branches** - deploy from main branch
- **Both services must auto-deploy** from main branch
- **Webhooks are critical** - without them, services get out of sync

### Files to Reference

1. **Main guide**: `/RAILWAY_COMPLETE_REBUILD_GUIDE.md` (follow this step-by-step)
2. **Environment template**: `/.env.example` (shows required variables)
3. **Frontend config**: `/vite.config.ts` (check proxy settings)
4. **CORS config**: Check `app/config.py` for CORS origins

### Verification Checklist

After setup, verify:
- [ ] Railway: All 3 services show green dots
- [ ] Vercel: Deployment successful
- [ ] GitHub: Both webhooks exist (Railway + Vercel)
- [ ] Railway `/health` returns "operational"
- [ ] Vercel frontend loads without CORS errors
- [ ] Login flow works (Firebase → Frontend → Backend)
- [ ] Auto-deploy works for BOTH services on git push

### Testing Full Integration

1. **Make a test commit**:
   ```bash
   echo "Test $(date)" > deployment-test.txt
   git add . && git commit -m "Test full deployment sync" && git push
   ```

2. **Watch both dashboards**:
   - Railway should start building
   - Vercel should start building
   - Both should complete successfully

3. **Test the full app**:
   - Visit Vercel frontend URL
   - Try to log in
   - Check browser console for any CORS errors
   - Verify API calls reach Railway backend

### Common Sync Issues

1. **Frontend can't reach backend**
   - Check VITE_API_URL in Vercel
   - Check CORS_ORIGINS in Railway
   - Must include exact Vercel URL

2. **Deploys out of sync**
   - Check both webhooks exist
   - Ensure both auto-deploy from main
   - Never deploy manually

3. **OAuth redirect fails**
   - Update Google OAuth to include both URLs:
     - Railway backend callback URL
     - Vercel frontend URL

### Expected Outcome

When complete:
- Single `git push` deploys both Railway backend and Vercel frontend
- No manual deployment needed
- Frontend and backend stay perfectly synchronized
- All features work: auth, API calls, background tasks

### Do NOT Skip

- Setting up BOTH webhooks (Railway + Vercel)
- Updating CORS_ORIGINS after getting Vercel URL
- Testing the complete auth flow
- Verifying both services auto-deploy together

## Summary of Steps

1. **DELETE everything first**:
   - All Railway projects named TTPROv4
   - All Vercel projects named TTPROv4
   - All webhooks in GitHub for this repo

2. **Follow setup guides**:
   - Read: https://github.com/kaseydoesmarketing/TTPROv4/blob/main/RAILWAY_COMPLETE_REBUILD_GUIDE.md
   - This has EVERYTHING you need for Railway setup

3. **Create fresh deployments**:
   - Railway: Backend API + PostgreSQL + Redis
   - Vercel: Frontend React app
   - Both connected to same GitHub repo

4. **Verify synchronization**:
   - One git push deploys BOTH services
   - No manual deployments needed
   - Everything stays in sync

**Start here**: https://github.com/kaseydoesmarketing/TTPROv4/blob/main/RAILWAY_COMPLETE_REBUILD_GUIDE.md