# DEVIN - FINAL BACKEND SETUP: Complete All Railway Services

## CURRENT STATUS SUMMARY

✅ **Web Service**: Fixed - All environment variables configured
❌ **Celery Beat**: Deploy failed - Missing service and environment variables
❌ **Celery Worker**: Deploy failed - Missing service and environment variables
✅ **PostgreSQL**: Running
✅ **Redis**: Running

**CRITICAL**: The A/B testing feature is BROKEN without Beat & Worker services!

## YOUR MISSION: Create and Configure Missing Celery Services

### STEP 1: CREATE CELERY BEAT SERVICE

1. **Go to Railway Dashboard**: https://railway.com/project/a4ed9479-2265-4e71-8378-1725357872f4
2. **Click "+ New"** button on the canvas
3. **Select "Empty Service"**
4. **Name it**: `beat`
5. **After creation, click on the Beat service**
6. **Go to Settings tab**:
   - **Source**: Connect to GitHub repo `kaseydoesmarketing/TTPROv4`
   - **Branch**: `main`
   - **Root Directory**: `/` (leave empty)
   - **Build Command**: (leave empty)
   - **Start Command**: `celery -A app.celery_app beat --loglevel=info`
   - **Auto Deploy**: ✅ ENABLED

### STEP 2: CREATE CELERY WORKER SERVICE

1. **Click "+ New"** button again
2. **Select "Empty Service"**
3. **Name it**: `worker`
4. **After creation, click on the Worker service**
5. **Go to Settings tab**:
   - **Source**: Connect to GitHub repo `kaseydoesmarketing/TTPROv4`
   - **Branch**: `main`
   - **Root Directory**: `/` (leave empty)
   - **Build Command**: (leave empty)
   - **Start Command**: `celery -A app.celery_app worker --loglevel=info`
   - **Auto Deploy**: ✅ ENABLED

### STEP 3: ADD ENVIRONMENT VARIABLES TO BEAT

Click on **Beat service** → **Variables** tab → **Raw Editor**

**Copy and paste ALL of these exactly:**

```env
DATABASE_URL=${{Postgres.DATABASE_URL}}
REDIS_URL=${{Redis.REDIS_URL}}
FIREBASE_PROJECT_ID=titletesterpro
FIREBASE_PRIVATE_KEY_ID=23f2eaa4a7f9d87335744ac68d95326e495b7cda
FIREBASE_PRIVATE_KEY=-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDVABbV93i24ViG\nEccVLrYtkWA/QPGLGeE4pIShFphqNEHWeJCfjPMIaVlemwtnSbu8SkxohovNoEwN\nhN3NM1PJmKcUOfDUTzD+m8n3/On8+PuRyxEuGAE1FFkdlSJFfN9XU0dU3VpfmmTm\nmAMF9YUS8Wya5gmwsPrr6mL5R4OSo655T1Ghig55YDXUy9eTTbR4FPXDwOhTlNoy\nqaBM8ml4djneXMrmkoF37vUGk7g0KbVQkjGOjlNX0n5L0Kl4XwRZDM1fIQgBIvk7\nAfzO1Bi048sXjGygS4eHVOohhA+VXxWQe7nwAVUu5no28Mz2QR2OWBgzE72s9VLz\ndYvRKdOdAgMBAAECggEAE22tJ49+9XYg5tBopNrRvN6ln/oSri9KTFTb+3zoonNU\nIrXKQfYPgE+/r5yb0dbiEWmDhls+FZ+j9ZhjdOFUKK93D1C+UgH2hEV94Clecc0y\nK9kRHu+17dCxKjzIAfztuvTlLO1TM3o37uf5tUmbqEqDhK4r6cUoNhb3N9QD69Q9\n/gLktKYjEEGTjR/FfvQ6nTKuhQeTbxkdICgzR5TE4PIhFW8DIrLtERDKKkJ3QhRr\n0Gz3XVmQZ0xwkr3bh0xs9W96kyZE+FrThqvlaGnYpw2D+V7kSvTWuH36LBUTRj4W\nFUellLMSAv3EHC75RoH2TCvPQhCwSi5XrvtOn6RUTwKBgQDxw8eiOojSb3UPEk3c\nNORFUXfyfRAUCmU26dEWVfDVDCU0xnjc8KvkgmnNT4BOnP9281UJqcKbhscL3WCb\nD5XrI0opc52SEynZydGxkUlCrNUcejfkiOZkCcSWALaZwa0EMzmAwgslQ24VPh6T\ngatrc6KKJi/9MjroXSVQpO8twwKBgQDhirtAVY934HcY2r7oC4zj6KszLlVkfcBn\np1FfPfx/5ppDcZNoncHocDK6kRH9yLZ+FHXUSwzkz1weyzTeLLft0BxqQ9qIZWRT\nY4m5H3fnljxjrQgA8Uv1CGEZmvp/K6nyGckOaxhH8SH4L0T5t/AoR/EkP+zHpNVq\nhfgOrg4DHwKBgQCeoUAGwPNvZ/RdvDvcJdQ1a1wRfl+jVqLMoiQvzJnloD91XliF\nV2Dh4XP8Y5Kjgj3Y1ZZRbdKj644Eye+OLm7GxvPtONAFvY8zOEnfgZ2ZIv/93G96\nAx1wPDyB09v8DOkyHU44npljjNfZFlZHoMhSC6B1ltLcBi5CsoM+Y8oPswKBgDUD\nErgwZCRdEiE5aR3JeTgoe/TvswqHtC2o2it0umClpySrEWbJjcZAeOv5JS1te9du\nn7NiYIl3Y8OpJ6gBAspW3BbuE/NzQX2IK9rjVp+MZG1ZQkRWcvAJJCmMj8xMSwmo\nneVRrsdaGg3nrmKzpTMSlc9bZyAV0kPTcVah+pEpAoGBAPFwQPoKrbVY0ZKdDmss\n1ouH/iSZ82M61cZJajv+xk4Eevxz92ROikTT5WQt15NGFk+d/t9cjYRpFcZyW+Q+\n4WL2oVPPRebOcqLTxr/0mwb2I35Km/fsiAiQw4jCXA3fg841yR/jEAa/bn7lm6KW\n63gKvnwbGLikocXDZ9anJJlp\n-----END PRIVATE KEY-----
FIREBASE_CLIENT_EMAIL=firebase-adminsdk-fbsvc@titletesterpro.iam.gserviceaccount.com
FIREBASE_CLIENT_ID=100530769397723070035
FIREBASE_AUTH_URI=https://accounts.google.com/o/oauth2/auth
FIREBASE_TOKEN_URI=https://oauth2.googleapis.com/token
FIREBASE_AUTH_PROVIDER_X509_CERT_URL=https://www.googleapis.com/oauth2/v1/certs
GOOGLE_CLIENT_ID=618794070994-0p4hlg4devshr6l6bkdh3c4l4oh34flp.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=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
YOUTUBE_API_KEY=AIzaSyBosbRgJxRTWJpSfIiEbDP8EmmRXY0FjF8
SECRET_KEY=your-super-secret-key-for-jwt-signing-and-encryption
ENVIRONMENT=production
```

**Click "Update Variables"**

### STEP 4: ADD ENVIRONMENT VARIABLES TO WORKER

Click on **Worker service** → **Variables** tab → **Raw Editor**

**Copy and paste the EXACT SAME variables as Beat** (all variables from Step 3)

**Click "Update Variables"**

### STEP 5: VERIFY ALL SERVICES ARE BUILDING

After adding variables:
1. Both Beat and Worker should start building automatically
2. Wait for builds to complete (3-5 minutes)
3. Check that all services show green dots

### STEP 6: FINAL VERIFICATION CHECKLIST

**Railway Dashboard Status:**
- [ ] Web: 🟢 Green dot
- [ ] PostgreSQL: 🟢 Green dot  
- [ ] Redis: 🟢 Green dot
- [ ] Beat: 🟢 Green dot
- [ ] Worker: 🟢 Green dot

**Health Check:**
```bash
curl https://web-production-98a4c.up.railway.app/health
```

Should return:
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

**Beat Service Logs** (click Beat → View Logs):
Should show:
```
[2025-08-04 16:30:00,000: INFO/MainProcess] beat: Starting...
[2025-08-04 16:30:00,000: INFO/MainProcess] Scheduler: Sending due task rotate-titles-robust
```

**Worker Service Logs** (click Worker → View Logs):
Should show:
```
[2025-08-04 16:30:01,000: INFO/MainProcess] Task app.robust_tasks.rotate_titles_robust received
[2025-08-04 16:30:02,000: INFO/MainProcess] Task app.robust_tasks.rotate_titles_robust succeeded
```

## TROUBLESHOOTING

### If Beat/Worker fail to deploy:

1. **Check Build Logs**: Look for missing dependencies
2. **Verify Start Command**: Must be exactly as specified
3. **Check Environment Variables**: All must be present
4. **Ensure GitHub Connection**: Both services must connect to same repo

### Common Errors:

**"Module not found"**: 
- Ensure root directory is `/` (empty)
- Check that GitHub repo is connected

**"Connection refused"**:
- Check DATABASE_URL and REDIS_URL are using Railway's reference syntax
- Should be: `${{Postgres.DATABASE_URL}}` not a hardcoded URL

**"Authentication failed"**:
- Verify Firebase private key has literal `\n` characters
- Check all Firebase variables are correct

## SUCCESS CRITERIA

✅ **All 5 services showing green dots in Railway**
✅ **Health endpoint returns "operational" status**
✅ **Beat logs show scheduled tasks running**
✅ **Worker logs show tasks being executed**
✅ **No errors in any service logs**

## CRITICAL IMPORTANCE

**Without Beat & Worker services:**
- ❌ No automatic YouTube title rotation
- ❌ No A/B test functionality  
- ❌ No background job processing
- ❌ Core feature completely broken

**These are NOT optional** - they are essential for the application to function!

## FINAL NOTES

- Use EXACT same environment variables for all services
- Don't modify start commands
- Ensure auto-deploy is enabled for all services
- All services must be on `main` branch

Once all 5 services show green dots, the backend is FULLY OPERATIONAL!

**Report back with the verification checklist completed.**