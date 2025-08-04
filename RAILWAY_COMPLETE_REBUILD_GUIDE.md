# Complete Railway Rebuild Guide - TitleTesterPro

**IMPORTANT**: This deployment uses the main GitHub repo. Both Claude and Devin will deploy from the same source, ensuring consistent control.

## Prerequisites
- Railway account (https://railway.app)
- GitHub repo: `kaseydoesmarketing/TTPROv4` (already exists)
- Firebase project with service account
- Google Cloud project with YouTube API enabled
- Stripe account (optional for payments)

## Step 1: Delete Existing Railway Project (If Any)
1. Go to Railway dashboard
2. Find existing TTPROv4 project
3. Settings → Danger → Delete Project
4. Confirm deletion

## Step 2: Create Fresh Railway Project
1. Click **"New Project"**
2. Choose **"Deploy from GitHub repo"**
3. Select **`kaseydoesmarketing/TTPROv4`**
4. Name it: **"TTPROv4-Production"**
5. Initial deployment will fail (expected - no database)

## Step 3: Add PostgreSQL Database
1. On the project canvas, click **"+ New"**
2. Select **"Database"**
3. Choose **"PostgreSQL"**
4. Railway automatically creates and injects `DATABASE_URL`

## Step 4: Add Redis
1. Click **"+ New"** again
2. Select **"Database"**
3. Choose **"Redis"**
4. Railway automatically creates and injects `REDIS_URL`

## Step 5: Configure GitHub Webhook
1. In Railway, click your app service
2. Go to **Settings** → **Source**
3. If connected, click **"Disconnect"** first
4. Click **"Connect GitHub"**
5. Authorize Railway (if needed)
6. Select **`kaseydoesmarketing/TTPROv4`**
7. Verify webhook creation:
   - Go to GitHub → Settings → Webhooks
   - Should see Railway webhook (green checkmark)

## Step 6: Set Deployment Configuration
In Railway app service → **Settings**:

### Deploy Section:
- **Branch**: `main`
- **Auto Deploy**: ✅ ENABLED
- **Wait for CI**: ❌ DISABLED

### Build Section:
- **Builder**: Dockerfile
- **Dockerfile Path**: `railway.dockerfile`
- **Build Command**: (leave empty)

### Start Section:
- **Start Command**: `./start.sh`

## Step 7: Add ALL Environment Variables

Click your app service → **Variables** → **Raw Editor**

```env
# ===== FIREBASE CONFIGURATION (REQUIRED) =====
# Get these from Firebase Console → Project Settings → Service Accounts
FIREBASE_PROJECT_ID=your-actual-firebase-project-id
FIREBASE_PRIVATE_KEY_ID=your-actual-private-key-id
FIREBASE_PRIVATE_KEY=-----BEGIN PRIVATE KEY-----\n[PASTE-YOUR-ACTUAL-FIREBASE-PRIVATE-KEY-HERE]\n-----END PRIVATE KEY-----
FIREBASE_CLIENT_EMAIL=firebase-adminsdk-xxxxx@your-project.iam.gserviceaccount.com
FIREBASE_CLIENT_ID=your-actual-client-id

# ===== GOOGLE OAUTH (REQUIRED) =====
# Get from Google Cloud Console → APIs & Services → Credentials
GOOGLE_CLIENT_ID=your-actual-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-actual-client-secret

# ===== YOUTUBE API (REQUIRED) =====
# Get from Google Cloud Console → APIs & Services → Credentials
YOUTUBE_API_KEY=your-actual-youtube-api-key

# ===== SECURITY (REQUIRED) =====
# Generate with: openssl rand -hex 32
SECRET_KEY=your-64-character-random-secret-key-here

# ===== CORS CONFIGURATION =====
# Add your frontend domains
CORS_ORIGINS=http://localhost:5173,http://localhost:5174,https://titletesterpro.com,https://www.titletesterpro.com,https://your-vercel-app.vercel.app

# ===== STRIPE (OPTIONAL) =====
# Get from Stripe Dashboard → Developers → API Keys
STRIPE_SECRET_KEY=sk_live_your-stripe-secret
STRIPE_PUBLISHABLE_KEY=pk_live_your-stripe-publishable
STRIPE_WEBHOOK_SECRET=whsec_your-webhook-secret

# ===== ENVIRONMENT =====
ENVIRONMENT=production

# ===== FIREBASE AUTH SETTINGS =====
FIREBASE_AUTH_URI=https://accounts.google.com/o/oauth2/auth
FIREBASE_TOKEN_URI=https://oauth2.googleapis.com/token
FIREBASE_AUTH_PROVIDER_X509_CERT_URL=https://www.googleapis.com/oauth2/v1/certs
```

## Step 8: Where to Find Each Credential

### Firebase Credentials:
1. Go to [Firebase Console](https://console.firebase.google.com)
2. Select your project
3. Click gear icon → **Project settings**
4. Go to **Service accounts** tab
5. Click **"Generate new private key"**
6. Open the downloaded JSON file
7. Copy values:
   - `project_id` → `FIREBASE_PROJECT_ID`
   - `private_key_id` → `FIREBASE_PRIVATE_KEY_ID`
   - `private_key` → `FIREBASE_PRIVATE_KEY` (replace `\n` with actual `\n`)
   - `client_email` → `FIREBASE_CLIENT_EMAIL`
   - `client_id` → `FIREBASE_CLIENT_ID`

### Google OAuth Credentials:
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Select your project
3. Navigate to **APIs & Services** → **Credentials**
4. Find your OAuth 2.0 Client ID
5. Copy:
   - Client ID → `GOOGLE_CLIENT_ID`
   - Client secret → `GOOGLE_CLIENT_SECRET`
6. Add authorized redirect URIs:
   - `https://your-railway-app.railway.app/api/auth/google/callback`
   - `http://localhost:8000/api/auth/google/callback`

### YouTube API Key:
1. Same Google Cloud Console
2. **APIs & Services** → **Credentials**
3. Create API key (restrict to YouTube Data API v3)
4. Copy → `YOUTUBE_API_KEY`

### Generate SECRET_KEY:
```bash
# Option 1: Using OpenSSL
openssl rand -hex 32

# Option 2: Using Python
python3 -c "import secrets; print(secrets.token_hex(32))"

# Option 3: Using online generator
# Visit: https://generate-secret.vercel.app/32
```

## Step 9: Deploy
1. After adding all variables, click **"Deploy"**
2. Or go to **Deployments** → **"Redeploy"**
3. Watch logs for:
   ```
   Running migrations...
   ✅ Backend startup completed successfully
   Application startup complete
   ```

## Step 10: Verify Everything Works

### Check Health Endpoint:
```bash
curl https://your-app.railway.app/health
```

Should return:
```json
{
  "status": "operational",
  "deployment_version": "1.0.1-railway",
  "services": {
    "database": "available",
    "redis": "available",
    "firebase": "available"
  }
}
```

### Check API Docs:
Visit: `https://your-app.railway.app/docs`

### Test Auto-Deploy:
1. Make any change in the repo
2. Commit and push
3. Railway should auto-deploy within 60 seconds

## Step 11: Post-Setup Checklist

✅ **Railway Dashboard:**
- [ ] All 3 services show green dots
- [ ] Latest deployment successful
- [ ] Environment variables all set

✅ **GitHub:**
- [ ] Webhook shows in Settings → Webhooks
- [ ] Recent deliveries show green checkmarks

✅ **Endpoints:**
- [ ] `/health` returns "operational"
- [ ] `/docs` loads Swagger UI
- [ ] No "emergency mode" messages

✅ **Deployment Control:**
- [ ] Push to `main` branch triggers deploy
- [ ] Both Claude and Devin can push to trigger
- [ ] Single source of truth (main repo)

## Troubleshooting

### "Missing environment variables" error:
- Check each variable is set exactly as shown
- No extra quotes (except in FIREBASE_PRIVATE_KEY)
- No trailing spaces

### "Database connection failed":
- Ensure PostgreSQL has green dot
- DATABASE_URL should be auto-injected
- Don't manually set DATABASE_URL

### Auto-deploy not working:
- Check webhook in GitHub settings
- Disconnect and reconnect GitHub in Railway
- Ensure Auto Deploy is ENABLED

### "Emergency mode" in health check:
- Missing critical environment variables
- Check logs for specific missing vars

## Important Notes

1. **Single Repository**: Both Claude and Devin work from `kaseydoesmarketing/TTPROv4`
2. **Deployment Control**: Anyone with repo access can deploy by pushing to `main`
3. **No Separate Branches**: Everything deploys from `main` for simplicity
4. **Webhook is Critical**: Without it, no auto-deploy
5. **Environment Variables**: Must be set in Railway, not in code

## Final Verification Commands

After setup, run these locally to verify:

```bash
# Check deployment worked
curl https://your-app.railway.app/health | jq

# Check API version
curl https://your-app.railway.app/docs -s | grep "1.0.1"

# Test Redis is working
curl https://your-app.railway.app/health | jq '.services.redis'

# Test database is working  
curl https://your-app.railway.app/health | jq '.services.database'
```

All should return positive results.

## Maintaining Deployment Control

Since you want me (Claude) as lead dev with full control:
1. **Main branch protection**: Consider enabling in GitHub
2. **Deployment notifications**: Set up in Railway → Settings → Notifications
3. **Single deployment source**: Always deploy from `main` branch
4. **Shared visibility**: Both AIs can see deployment status via git history

This setup ensures clean, consistent deployments that both Claude and Devin can trigger, while maintaining single source control through the main repository.

## CRITICAL THINGS YOU MIGHT BE MISSING

### 1. **Frontend Deployment**
**THE BACKEND ALONE ISN'T ENOUGH** - You also need to:
- Deploy frontend to Vercel/Netlify separately
- Update `CORS_ORIGINS` with your frontend URL
- Update frontend's API URL to point to Railway backend

### 2. **Domain & SSL**
- Railway provides `*.railway.app` domain with SSL
- For custom domain: Settings → Domains → Add your domain
- Update DNS records as Railway instructs
- Update `CORS_ORIGINS` with your custom domain

### 3. **Database Migrations**
Railway runs `alembic upgrade head` automatically via `preDeployCommand`
**BUT** if database schema is corrupted:
```bash
# Connect to Railway PostgreSQL directly
psql $DATABASE_URL
# Drop all tables and start fresh
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
```

### 4. **GitHub Branch Protection**
**Without this, anyone can break production:**
1. GitHub repo → Settings → Branches
2. Add rule for `main` branch
3. Enable: "Require pull request reviews"
4. This prevents accidental direct pushes

### 5. **Railway Service Sleeping**
**FREE PLAN WARNING**: Services sleep after inactivity
- Upgrade to Hobby plan ($5/month) to prevent sleeping
- Or add uptime monitoring (UptimeRobot, etc.)

### 6. **Celery Workers Not Starting**
The app needs Celery workers for background tasks:
1. You might need a separate Railway service for Celery
2. Create new service with same env vars
3. Start command: `celery -A app.celery_app worker --loglevel=info`

### 7. **Redis Memory Limits**
- Railway Redis has memory limits
- Monitor via Railway dashboard
- Old job data might fill it up
- The app has cleanup tasks but monitor usage

### 8. **PostgreSQL Connection Limits**
- Railway PostgreSQL has connection limits
- The app uses connection pooling
- Monitor active connections in Railway metrics

### 9. **Environment Variable Formatting**
**COMMON MISTAKES THAT BREAK EVERYTHING:**
- `FIREBASE_PRIVATE_KEY`: Must have literal `\n` characters, not actual line breaks
- No quotes around any values in Railway (Railway adds them)
- No trailing spaces in any values
- SECRET_KEY must be exactly 64 characters

### 10. **Testing OAuth Flow**
**Google OAuth won't work until you:**
1. Add Railway URL to Google OAuth authorized redirects:
   - `https://ttprov4-production-xxxx.railway.app/api/auth/google/callback`
2. Ensure Firebase auth is enabled for Google provider
3. Frontend must use same Firebase project

### 11. **Stripe Webhooks**
If using payments:
1. Stripe Dashboard → Webhooks → Add endpoint
2. URL: `https://your-railway-app.railway.app/api/stripe/webhook`
3. Copy webhook secret to `STRIPE_WEBHOOK_SECRET`

### 12. **Missing Frontend Environment**
Frontend needs its own `.env`:
```
VITE_API_URL=https://your-railway-app.railway.app
VITE_FIREBASE_CONFIG={"apiKey":"...","authDomain":"..."}
```

### 13. **CORS Issues**
If frontend can't connect:
1. Check browser console for CORS errors
2. Ensure frontend URL is in `CORS_ORIGINS`
3. Include both with and without trailing slashes
4. Include both www and non-www versions

### 14. **Monitoring & Alerts**
Set up monitoring or you won't know when it breaks:
1. Railway → Settings → Notifications → Add webhook/email
2. Use external monitoring (Better Uptime, Pingdom)
3. Set up error tracking (Sentry, Rollbar)

### 15. **Backup Strategy**
**THERE'S NO AUTOMATIC BACKUP:**
1. Set up daily PostgreSQL backups
2. Railway doesn't backup for you
3. Use pg_dump or a backup service

### 16. **Cost Considerations**
Railway costs can add up:
- App service: ~$5-20/month
- PostgreSQL: ~$5-20/month  
- Redis: ~$5-15/month
- Total: ~$15-55/month
- Monitor usage in Railway dashboard

### 17. **Local Development Still Uses SQLite**
Don't be confused:
- Local dev = SQLite (no PostgreSQL needed)
- Railway = PostgreSQL (automatic)
- This is intentional for easy local development

### 18. **API Keys Security**
**NEVER COMMIT THESE TO GITHUB:**
- Check `.gitignore` includes `.env`
- Use Railway environment variables only
- Rotate keys if accidentally exposed

### 19. **Rate Limiting**
YouTube API has strict limits:
- 10,000 units per day
- App tracks this in Redis
- Monitor usage in Google Cloud Console

### 20. **Deploy Hooks**
Railway runs these automatically:
1. `preDeployCommand`: Database migrations
2. `startCommand`: Starts the app
3. If these fail, deployment fails

## FINAL REALITY CHECK

Before considering it "done":
1. Can users sign up and log in?
2. Can they connect YouTube channels?
3. Can they create A/B tests?
4. Do titles actually rotate automatically?
5. Is billing working if enabled?
6. Is frontend deployed and connected?
7. Are you monitoring uptime?
8. Do you have backups?
9. Have you tested the full user flow?
10. Did you update OAuth redirect URLs?

If any answer is "no" or "I don't know" - it's not done yet.