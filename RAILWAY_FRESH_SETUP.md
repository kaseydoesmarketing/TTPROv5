# Fresh Railway Setup Instructions for Devin

## Overview
Set up TTPROv4 on Railway with PostgreSQL, Redis, and automatic deployments.

## Step-by-Step Instructions

### 1. Create New Railway Project
- Go to https://railway.app
- Click "New Project"
- Select "Deploy from GitHub repo"
- Choose "TTPROv4" repository
- Let initial deployment fail (normal - no database yet)

### 2. Add PostgreSQL Service
- Click "+" button on canvas
- Select "Database" → "PostgreSQL"
- Wait for provisioning (~30 seconds)
- PostgreSQL will auto-inject DATABASE_URL

### 3. Add Redis Service  
- Click "+" button again
- Select "Database" → "Redis"
- Wait for provisioning (~30 seconds)
- Redis will auto-inject REDIS_URL

### 4. Configure Environment Variables
Click on your app service → Variables tab → Raw Editor
Add these (DATABASE_URL and REDIS_URL should already be there):

```env
FIREBASE_PROJECT_ID=titletesterpro
FIREBASE_PRIVATE_KEY_ID=get-from-firebase-console
FIREBASE_PRIVATE_KEY=-----BEGIN PRIVATE KEY-----\nget-from-firebase-console\n-----END PRIVATE KEY-----
FIREBASE_CLIENT_EMAIL=get-from-firebase-console
FIREBASE_CLIENT_ID=get-from-firebase-console
GOOGLE_CLIENT_ID=get-from-google-cloud-console
GOOGLE_CLIENT_SECRET=get-from-google-cloud-console
YOUTUBE_API_KEY=get-from-google-cloud-console
SECRET_KEY=generate-random-64-character-string-here
CORS_ORIGINS=https://titletesterpro.com,https://www.titletesterpro.com
ENVIRONMENT=production
```

### 5. Configure Deployment Settings
- Go to Settings tab
- Under "Deploy":
  - Branch: main
  - Auto Deploy: ENABLED ✓
  - Wait for CI: DISABLED ✗ (no GitHub Actions)
- Under "Build":
  - Builder: Dockerfile
  - Dockerfile Path: railway.dockerfile

### 6. Verify GitHub Webhook
- Go to GitHub repo → Settings → Webhooks
- Should see Railway webhook (auto-created)
- If not, reconnect GitHub in Railway Settings

### 7. Deploy
- Click "Redeploy" on latest deployment
- Watch logs for:
  - "Running migrations"
  - "Application startup complete"
  - No red errors

### 8. Verify Deployment
- Visit: https://[your-app].railway.app/health
- Should show:
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

### 9. Test Auto-Deploy
- Make small change to any file
- Commit and push
- Railway should auto-deploy within 1-2 minutes

## Required External Services

### Firebase Setup
1. Create Firebase project
2. Enable Authentication
3. Generate service account key
4. Copy values to Railway environment variables

### Google Cloud Setup  
1. Enable YouTube Data API v3
2. Create OAuth 2.0 credentials
3. Add authorized redirect URIs
4. Copy client ID/secret to Railway

### Stripe Setup (Optional)
1. Create Stripe account
2. Get API keys from dashboard
3. Set up webhook endpoint
4. Add keys to Railway environment variables

## Troubleshooting

### "Missing environment variables"
- Double-check all required vars are set
- No quotes around values (except FIREBASE_PRIVATE_KEY)

### "Database connection failed"
- Ensure PostgreSQL service is running (green dot)
- DATABASE_URL should be auto-set by Railway

### "Redis unavailable"
- Ensure Redis service is running (green dot)
- REDIS_URL should be auto-set by Railway

### Auto-deploy not working
- Check Settings → Deploy → Auto Deploy is ON
- Verify GitHub webhook exists and is active
- Try disconnect/reconnect GitHub

## Success Criteria
✅ All services show green dots
✅ Health endpoint returns "operational"
✅ Git pushes trigger automatic deployments
✅ Frontend can connect to API
✅ Background tasks (Celery) are processing

## Notes
- The app uses SQLite fallback if PostgreSQL fails (dev only)
- Redis is required for background job processing
- All sensitive keys must be kept secret
- Use .env.example as reference for required variables