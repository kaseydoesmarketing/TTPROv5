# TitleTesterPro Operations Runbook

## Quick Reference Guide for Common Operations

### Adding a New Vercel Preview to Firebase Domains

1. Go to [Firebase Console](https://console.firebase.google.com)
2. Navigate to Authentication → Settings → Authorized domains
3. Click "Add domain"
4. Add your Vercel preview URL (e.g., `ttprov5-abc123.vercel.app`)
5. Save changes
6. Test authentication on the preview URL

### Rotating Stripe Keys/Webhook Secret Safely

1. **Generate new keys in Stripe Dashboard**
   - Go to Stripe Dashboard → Developers → API keys
   - Create new secret key (keep old one active)
   
2. **Update Render environment variables**
   - Set `STRIPE_SECRET_KEY` to new value
   - Keep old key active in Stripe during transition
   
3. **For webhook secret rotation:**
   - Create new webhook endpoint in Stripe
   - Update `STRIPE_WEBHOOK_SECRET` in Render
   - Test new webhook with Stripe CLI
   - Disable old webhook endpoint after verification

4. **Verification:**
   - Test a checkout session
   - Verify webhook events are received
   - Check logs for any authentication errors
   
5. **Cleanup:**
   - Revoke old API key in Stripe
   - Remove old webhook endpoint

### Restarting Celery Worker/Beat on Render

1. **Via Render Dashboard:**
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Select the worker service (`ttpro-celery` or `ttpro-celery-beat`)
   - Click "Manual Deploy" → "Clear build cache & deploy"
   
2. **Force restart without redeploy:**
   - Click on the service
   - Go to "Settings" tab
   - Click "Restart Service"

3. **Monitoring:**
   - Check service logs for startup confirmation
   - Look for: `celery@<hostname> ready` message
   - Verify beat scheduler shows: `beat: Starting...`

### Running Smoke Tests

1. **Basic smoke test:**
   ```bash
   ./scripts/smoke.sh
   ```

2. **Test specific environment:**
   ```bash
   ./scripts/smoke.sh https://ttprov4-k58o.onrender.com https://www.titletesterpro.com
   ```

3. **What success looks like:**
   - CORS header present: `access-control-allow-origin: https://www.titletesterpro.com`
   - Health status: `"healthy"`
   - Auth endpoint returns: `HTTP/1.1 401 Unauthorized` (expected for unauthenticated request)

4. **Common failures and fixes:**
   - No CORS header: Check CORS configuration in backend
   - 502/503 errors: Backend service is down, check Render logs
   - Connection refused: Check API URL and network connectivity

### Emergency Procedures

#### Backend is Down
1. Check Render service status
2. Look for recent deploys that might have broken
3. Rollback to previous version if needed
4. Check database connectivity
5. Verify environment variables are set

#### Authentication Broken
1. Verify Firebase credentials in Render
2. Check Firebase authorized domains
3. Verify frontend is sending correct auth headers
4. Check Firebase Console for any service issues

#### Database Connection Lost
1. Check DATABASE_URL in Render
2. Verify PostgreSQL service is running
3. Check connection pool settings
4. Look for connection limit issues
5. Restart backend service if needed

#### Background Jobs Not Processing
1. Check Redis connection (`REDIS_URL`)
2. Verify Celery worker is running
3. Check Celery beat for scheduled tasks
4. Look for task exceptions in worker logs
5. Clear Redis queue if corrupted

### Monitoring Checklist

Daily:
- [ ] Check health endpoint
- [ ] Verify background jobs are processing
- [ ] Review error logs for patterns

Weekly:
- [ ] Review Stripe webhook success rate
- [ ] Check database performance metrics
- [ ] Verify backup status

Monthly:
- [ ] Rotate API keys (if needed)
- [ ] Review and update authorized domains
- [ ] Check for dependency updates
- [ ] Review resource usage and costs