# DEVIN - Complete Railway Deployment with Celery Services

## CURRENT STATUS

**Main Web Service**: ✅ Fixed - All 18 environment variables configured, deployment building
**Celery Beat**: ❌ Deploy failed - Missing environment variables  
**Celery Worker**: ❌ Deploy failed - Missing environment variables

## WHAT ARE BEAT & WORKER?

These are **CRITICAL** background services for TitleTesterPro:

### Celery Beat (Scheduler)
- **Purpose**: Schedules periodic tasks
- **Critical Task**: Rotates YouTube titles every minute for A/B tests
- **Without it**: No automatic title rotation (core feature broken)

### Celery Worker (Task Processor)
- **Purpose**: Executes background tasks
- **Critical Tasks**: 
  - `rotate_titles` - Changes YouTube video titles
  - `update_quota_usage` - Tracks API usage
  - `refresh_tokens` - Keeps OAuth tokens valid
- **Without it**: No background processing works

## YOUR TASK

### 1. Fix Celery Beat Service
1. Go to Railway dashboard
2. Click on **"beat"** service (showing failed)
3. Go to **Variables** tab
4. Add ALL the same environment variables you added to the web service:

```env
FIREBASE_PROJECT_ID=titletesterpro
FIREBASE_PRIVATE_KEY_ID=23f2eaa4a7f9d87335744ac68d95326e495b7cda
FIREBASE_PRIVATE_KEY=-----BEGIN PRIVATE KEY-----\n[FULL KEY WITH LITERAL \n]
FIREBASE_CLIENT_EMAIL=firebase-adminsdk-fbsvc@titletesterpro.iam.gserviceaccount.com
FIREBASE_CLIENT_ID=100530769397723070035
FIREBASE_AUTH_URI=https://accounts.google.com/o/oauth2/auth
FIREBASE_TOKEN_URI=https://oauth2.googleapis.com/token
FIREBASE_AUTH_PROVIDER_X509_CERT_URL=https://www.googleapis.com/oauth2/v1/certs
GOOGLE_CLIENT_ID=618794070994-0p4hlg4devshr6l6bkdh3c4l4oh34flp.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=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
YOUTUBE_API_KEY=AIzaSyBosbRgJxRTWJpSfIiEbDP8EmmRXY0FjF8
SECRET_KEY=your-super-secret-key-for-jwt-signing-and-encryption
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,http://localhost:5174,https://ttprov4.vercel.app,https://titletesterpro.com
ENVIRONMENT=production
```

5. **CRITICAL**: Beat also needs Redis URL - Railway should auto-inject:
   - `REDIS_URL` (from Redis service)
   - `DATABASE_URL` (from PostgreSQL service)

### 2. Fix Celery Worker Service
1. Click on **"worker"** service (showing failed)
2. Go to **Variables** tab
3. Add the SAME environment variables as above
4. Ensure `REDIS_URL` and `DATABASE_URL` are present

### 3. Configure Service Settings

**For BOTH Beat and Worker services:**

1. Go to **Settings** tab
2. Check **Start Command**:
   - Beat should have: `celery -A app.celery_app beat --loglevel=info`
   - Worker should have: `celery -A app.celery_app worker --loglevel=info`

3. Ensure **Deploy** settings:
   - Branch: `main`
   - Auto Deploy: ✅ ENABLED

### 4. Verify All Services Running

After adding variables to both services:

1. **Check Railway Dashboard**:
   - Web service: 🟢 Green (running)
   - PostgreSQL: 🟢 Green (running)
   - Redis: 🟢 Green (running)
   - Beat: 🟢 Green (running)
   - Worker: 🟢 Green (running)

2. **Test Health Endpoint**:
   ```
   https://web-production-98a4c.up.railway.app/health
   ```
   Should show `"status": "operational"`

3. **Verify Background Tasks**:
   - Check logs for Beat service - should show scheduled tasks
   - Check logs for Worker service - should show task execution

## CRITICAL INFORMATION

**Without Beat & Worker**:
- ❌ No automatic title rotation
- ❌ No background job processing
- ❌ No API quota tracking
- ❌ No token refresh
- ❌ A/B testing feature completely broken

**These are NOT optional** - they're core to the application functionality.

## SUCCESS CRITERIA

✅ All 5 Railway services showing green dots
✅ Health endpoint returns "operational"
✅ Beat logs show scheduled tasks running
✅ Worker logs show task execution
✅ No "emergency" or "failed" status anywhere

## REFERENCE FILES

- Celery configuration: `app/celery_app.py`
- Task definitions: `app/tasks.py`, `app/robust_tasks.py`
- Job manager: `app/job_manager.py`

**IMPORTANT**: Use the exact same environment variables for all three services (web, beat, worker) to ensure they can all connect to the same Firebase, database, and Redis instances.