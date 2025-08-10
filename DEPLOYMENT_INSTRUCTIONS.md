# TTPROv5 Backend Deployment Instructions

## 🎯 READY FOR DEPLOYMENT

All code changes are complete and pushed to branch `fix/ttprov5-backend-redeploy-20250810_121500`.

## 📋 DEPLOYMENT CHECKLIST

### 1. Render Backend Deployment (NEW TTPROv5 Service)

**Environment Variables to Set:**
```bash
ENVIRONMENT=production
LOG_LEVEL=info
APP_NAME=titletesterpro

# Database & Redis (Internal URLs)
DATABASE_URL=postgresql://postgres_ttprov5_user:VE1ODbnInDCjcThgm4UVqWBNKU6GYK1n@dpg-d2cb900gjohc73fv7h60-a.virginia-postgres.render.com/postgres_ttprov5
REDIS_URL=redis://red-d2cbelf5iees73fgg71g:6379

# Firebase Admin (Secret File)
GOOGLE_APPLICATION_CREDENTIALS=/etc/secrets/firebase-key.json
ALLOW_ENV_FALLBACK=0
FIREBASE_DEBUG=1  # Temporarily set to 1 for verification, then set back to 0

# Google OAuth (Backend)
GOOGLE_CLIENT_ID=618794070994-70oauf1olrgmqvg284mpj5u2lf75jl1q.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=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
GOOGLE_API_KEY=AIzaSyA8hjvKfC_D1rQqIWgjhxq-xM1cmgDB3z4

# JWT Secret
JWT_SECRET_KEY=bB9uYvA4X7cP3fN2rL6mQ8tH1jR5wK0zS5dM7pV9qT2yU8gE1cL0bF4nJ6rQ2aW7

# Stripe (Test Keys)
STRIPE_SECRET_KEY=sk_test_xxx
STRIPE_PUBLISHABLE_KEY=pk_test_xxx

# CORS Origins
CORS_ORIGINS=https://www.titletesterpro.com,https://titletesterpro.com,https://*.vercel.app,http://localhost:5173
```

**Secret File to Add:**
- Path: `firebase-key.json`
- Content: The complete Firebase service account JSON from your file

**Deployment Steps:**
1. Configure all environment variables above
2. Add Firebase service account as Secret File
3. Deploy from branch `fix/ttprov5-backend-redeploy-20250810_121500`
4. Wait for deployment to complete
5. Note the new backend URL (e.g., `https://ttprov5-api.onrender.com`)

### 2. Vercel Frontend Update

**After backend is deployed:**
```bash
# Update environment variables with new backend URL
cd /Users/kvimedia/TTPROv5
./scripts/update-vercel-env.sh https://YOUR_NEW_BACKEND_URL.onrender.com

# Deploy frontend
vercel --prod --token pTlRlJaadobG5ZwoHUzjFoUb --scope ttpro-live
```

### 3. E2E Validation

**With Debug ON (FIREBASE_DEBUG=1):**
```bash
# Test debug endpoints
curl https://YOUR_BACKEND_URL/debug/firebase
# Should return configuration details

# Run E2E tests
BACKEND_URL=https://YOUR_BACKEND_URL FRONTEND_URL=https://titletesterpro.com npx playwright test e2e/auth-and-dashboard.spec.ts
```

**Then Debug OFF (FIREBASE_DEBUG=0):**
```bash
# Set FIREBASE_DEBUG=0 in Render environment variables
# Redeploy backend

# Test debug endpoints return 404
curl https://YOUR_BACKEND_URL/debug/firebase
# Should return 404

# Run E2E tests again to confirm lockdown
BACKEND_URL=https://YOUR_BACKEND_URL FRONTEND_URL=https://titletesterpro.com npx playwright test e2e/auth-and-dashboard.spec.ts
```

### 4. Background Workers (Optional)

**Create Celery Worker Service:**
- Type: Background Worker
- Start Command: `celery -A app.celery_app worker --loglevel=info`
- Environment: Same as main backend service

**Create Celery Beat Service:**
- Type: Background Worker  
- Start Command: `celery -A app.celery_app beat --loglevel=info --pidfile=`
- Environment: Same as main backend service

## ⚡ QUICK DEPLOYMENT

If you want to deploy immediately:

1. **Deploy Backend:** Go to Render → TTPROv5 backend service → Settings → connect to this branch
2. **Update Frontend:** Run `./scripts/update-vercel-env.sh https://YOUR_NEW_BACKEND_URL`  
3. **Test:** Run the E2E tests to verify everything works

## 📋 SUCCESS CRITERIA

All of these must pass before declaring success:

- ✅ `/healthz` returns `{"ok": true}`
- ✅ `/debug/firebase` shows `SECRET_FILE` configuration (when DEBUG=1)
- ✅ `/debug/firebase` returns 404 (when DEBUG=0)
- ✅ Authentication flow works end-to-end
- ✅ CORS allows requests from titletesterpro.com
- ✅ Session cookies have proper attributes
- ✅ All E2E tests pass

## 🎉 READY TO GO!

The code is production-ready. Just deploy the backend to your new TTPROv5 Render service and update the frontend URL!