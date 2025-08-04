# STRICT DEPLOYMENT INSTRUCTIONS FOR DEVIN - NO DEVIATIONS

**⚠️ CRITICAL: Follow these instructions EXACTLY. Do not improvise or skip steps. If unclear about ANYTHING, stop and ask for clarification.**

## Repository Information
- **GitHub URL**: https://github.com/kaseydoesmarketing/TTPROv4
- **Branch**: main (DO NOT create other branches)
- **Your Task**: Deploy backend on Railway, frontend on Vercel

## ⛔ STOP - DELETE EVERYTHING FIRST

### Step 1: Delete All Existing Projects
**DO THIS BEFORE ANYTHING ELSE:**

1. **Railway**: 
   - Go to Railway dashboard
   - Find ANY project with "TTPROv4" in the name
   - Settings → Danger Zone → Delete Project → Type project name → Confirm
   - ✅ VERIFY: No TTPROv4 projects remain

2. **Vercel**:
   - Go to Vercel dashboard
   - Find ANY project with "TTPROv4" in the name
   - Settings → Advanced → Delete Project → Type "delete" → Confirm
   - ✅ VERIFY: No TTPROv4 projects remain

3. **GitHub Webhooks**:
   - Go to: https://github.com/kaseydoesmarketing/TTPROv4/settings/hooks
   - DELETE all webhooks (Railway, Vercel, any others)
   - ✅ VERIFY: Webhooks page is empty

**🛑 CHECKPOINT 1**: All old projects deleted? Webhooks cleared? Only proceed if YES to both.

---

## 📋 PART 1: RAILWAY BACKEND SETUP

### Step 2: Create New Railway Project

1. Go to Railway dashboard
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose **`kaseydoesmarketing/TTPROv4`** (NOT a fork)
5. Name it: **"TTPROv4-Production"**
6. Let it fail to deploy (this is normal - no database yet)

**✅ VERIFY**: You see a failed deployment for TTPROv4-Production

### Step 3: Add PostgreSQL Database

1. On Railway canvas, click **"+ New"** 
2. Select **"Database"**
3. Click **"PostgreSQL"**
4. Wait for green checkmark (30-60 seconds)

**✅ VERIFY**: PostgreSQL box shows green dot

### Step 4: Add Redis Database

1. Click **"+ New"** again
2. Select **"Database"**
3. Click **"Redis"**
4. Wait for green checkmark (30-60 seconds)

**✅ VERIFY**: Redis box shows green dot

### Step 5: Configure Your App Service

1. Click on your app service (NOT PostgreSQL or Redis)
2. Go to **"Settings"** tab
3. Set these EXACTLY:

**Deploy Section:**
- Root Directory: `/` (leave empty)
- Branch: `main`
- Auto Deploy: **✅ ENABLED** (MUST be checked)
- Wait for CI: **❌ DISABLED** (MUST be unchecked)

**Build Section:**
- Builder: **Dockerfile**
- Dockerfile Path: `railway.dockerfile`

**✅ VERIFY**: All settings match above EXACTLY

### Step 6: Add Environment Variables

1. Stay in your app service
2. Click **"Variables"** tab
3. You should see `DATABASE_URL` and `REDIS_URL` already there
4. Click **"Raw Editor"**
5. ADD these lines EXACTLY (replace with real values):

```
# COPY EVERYTHING BELOW THIS LINE
FIREBASE_PROJECT_ID=titletesterpro
FIREBASE_PRIVATE_KEY_ID=abc123def456ghi789
FIREBASE_PRIVATE_KEY=-----BEGIN PRIVATE KEY-----\n[PASTE-YOUR-ACTUAL-FIREBASE-PRIVATE-KEY-HERE]\n-----END PRIVATE KEY-----
FIREBASE_CLIENT_EMAIL=firebase-adminsdk-xxxxx@titletesterpro.iam.gserviceaccount.com
FIREBASE_CLIENT_ID=123456789012345678901
FIREBASE_AUTH_URI=https://accounts.google.com/o/oauth2/auth
FIREBASE_TOKEN_URI=https://oauth2.googleapis.com/token
FIREBASE_AUTH_PROVIDER_X509_CERT_URL=https://www.googleapis.com/oauth2/v1/certs
GOOGLE_CLIENT_ID=123456789012-abcdefghijklmnop.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-1234567890abcdefghijk
YOUTUBE_API_KEY=AIzaSyD-1234567890abcdefghijklmnop
SECRET_KEY=64-character-hex-string-generate-with-openssl-rand-hex-32
ENVIRONMENT=production
CORS_ORIGINS=http://localhost:5173,http://localhost:5174,https://ttprov4.vercel.app
```

**⚠️ CRITICAL FORMATTING RULES:**
- NO quotes around any values
- NO extra spaces at the end of lines
- FIREBASE_PRIVATE_KEY must have literal `\n` (not actual line breaks)
- SECRET_KEY must be exactly 64 characters

6. Click **"Update Variables"**

**🛑 CHECKPOINT 2**: 
- [ ] PostgreSQL has green dot?
- [ ] Redis has green dot?
- [ ] All environment variables added?
- [ ] Auto-deploy is ENABLED?

### Step 7: Verify GitHub Webhook

1. Go to: https://github.com/kaseydoesmarketing/TTPROv4/settings/hooks
2. You should see a NEW Railway webhook
3. Click on it
4. Should show recent delivery with green checkmark

**✅ VERIFY**: Railway webhook exists and is active

### Step 8: Deploy Backend

1. Back in Railway, go to your app service
2. Click **"Deployments"** tab
3. Click **"Redeploy"** on the latest deployment
4. Watch the logs - look for:
   - "Running migrations"
   - "Application startup complete"
   - NO red error messages

**✅ VERIFY**: Deployment succeeds with green checkmark

### Step 9: Test Backend

1. Copy your Railway URL (shown in Settings → Domains)
2. Visit: `https://your-app.railway.app/health`
3. Should see:
```json
{
  "status": "operational",
  "services": {
    "database": "available",
    "redis": "available",
    "firebase": "available"
  }
}
```

**🛑 CHECKPOINT 3**: Health endpoint shows "operational"? If not, check environment variables.

---

## 📋 PART 2: VERCEL FRONTEND SETUP

### Step 10: Create Vercel Project

1. Go to Vercel dashboard
2. Click **"Add New Project"**
3. Import Git Repository
4. Select **`kaseydoesmarketing/TTPROv4`** (same repo)
5. Configure:
   - Framework Preset: **Vite**
   - Root Directory: **`.`** (leave as is)
   - Build Command: `npm run build`
   - Output Directory: `dist`
   - Install Command: `npm install`

### Step 11: Add Frontend Environment Variables

**BEFORE DEPLOYING**, add these environment variables in Vercel:

```
VITE_API_URL=https://your-railway-backend.railway.app
VITE_FIREBASE_API_KEY=same-as-backend-YOUTUBE_API_KEY
VITE_FIREBASE_AUTH_DOMAIN=titletesterpro.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=titletesterpro
VITE_FIREBASE_STORAGE_BUCKET=titletesterpro.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=123456789012
VITE_FIREBASE_APP_ID=1:123456789012:web:abcdef123456
```

**⚠️ IMPORTANT**: 
- Replace `your-railway-backend.railway.app` with your ACTUAL Railway URL
- Use the SAME Firebase values as backend

### Step 12: Deploy Frontend

1. Click **"Deploy"**
2. Wait for build to complete
3. Should see green checkmark

**✅ VERIFY**: Vercel deployment successful

### Step 13: Update Railway CORS

**CRITICAL - GO BACK TO RAILWAY:**

1. Copy your Vercel URL (e.g., `https://ttprov4.vercel.app`)
2. Go to Railway app service → Variables
3. UPDATE the CORS_ORIGINS to include your Vercel URL:
```
CORS_ORIGINS=http://localhost:5173,http://localhost:5174,https://ttprov4.vercel.app,https://your-custom-domain.com
```
4. Click **"Update Variables"**
5. Railway will auto-redeploy

**🛑 CHECKPOINT 4**: 
- [ ] Frontend deployed on Vercel?
- [ ] Backend CORS updated with Vercel URL?
- [ ] Both services show green/successful?

---

## 📋 PART 3: FINAL VERIFICATION

### Step 14: Test Full Integration

1. Visit your Vercel frontend URL
2. Open browser console (F12)
3. Try to log in with Google
4. Check for:
   - NO CORS errors in console
   - Login redirects properly
   - API calls succeed

### Step 15: Test Auto-Deploy Sync

1. Make a small change locally:
```bash
echo "Deployment test $(date)" > test-deploy.txt
git add test-deploy.txt
git commit -m "Test auto-deploy sync"
git push origin main
```

2. Watch BOTH dashboards:
   - Railway should start building
   - Vercel should start building
   - Both should complete successfully

**✅ FINAL VERIFICATION**:
- [ ] Frontend loads without errors
- [ ] Login with Google works
- [ ] No CORS errors in browser console
- [ ] Git push triggers BOTH deployments
- [ ] Health endpoint shows all services "available"

---

## ⚠️ COMMON MISTAKES TO AVOID

1. **DO NOT** create separate forks or branches
2. **DO NOT** manually deploy - use auto-deploy
3. **DO NOT** skip deleting old projects first
4. **DO NOT** forget to update CORS after getting Vercel URL
5. **DO NOT** use actual line breaks in FIREBASE_PRIVATE_KEY
6. **DO NOT** add quotes around environment variables
7. **DO NOT** proceed if webhooks aren't created

## 🆘 WHEN TO ASK FOR HELP

**STOP and ask for help if:**
- Any verification step fails
- You see errors you don't understand
- Auto-deploy doesn't trigger
- CORS errors appear
- Environment variables seem wrong
- Webhooks aren't created automatically
- You're unsure about ANY step

## 📝 FINAL CHECKLIST

Before marking complete, verify:

- [ ] Deleted all old Railway projects
- [ ] Deleted all old Vercel projects  
- [ ] Deleted all old webhooks
- [ ] Railway has PostgreSQL + Redis + App (all green)
- [ ] Vercel frontend deployed successfully
- [ ] GitHub shows both webhooks (Railway + Vercel)
- [ ] Health endpoint returns "operational"
- [ ] Frontend can connect to backend (no CORS)
- [ ] Google login works end-to-end
- [ ] Single git push deploys both services

**🎯 SUCCESS CRITERIA**: 
One `git push` to main branch triggers BOTH Railway and Vercel to deploy automatically, and the full application works with login, API calls, and background tasks.

---

**REMEMBER**: If anything is unclear or doesn't work as described, STOP and ASK for clarification. Do not guess or improvise.