# Operations Runbook

## Adding Vercel Preview to Firebase

When deploying a new Vercel preview branch:

1. Go to [Firebase Console](https://console.firebase.google.com)
2. Select the `titletesterpro` project
3. Navigate to **Authentication** → **Settings** → **Authorized domains**
4. Click **Add domain**
5. Enter your Vercel preview URL (e.g., `ttprov5-abc123.vercel.app`)
6. Save the changes
7. Test authentication on the preview URL

## Rotating Stripe Secrets

To safely rotate Stripe API keys:

### 1. Generate New Keys
- Go to Stripe Dashboard → Developers → API keys
- Create new secret key
- Keep old key active during transition

### 2. Update Environment Variables
- In Render dashboard, update `STRIPE_SECRET_KEY`
- Deploy the change
- Test payment functionality

### 3. Rotate Webhook Secret
- In Stripe Dashboard → Webhooks
- Create new webhook endpoint with new secret
- Update `STRIPE_WEBHOOK_SECRET` in Render
- Test webhook with Stripe CLI: `stripe listen --forward-to localhost:8000/api/billing/webhook`
- Remove old webhook endpoint

### 4. Cleanup
- After confirming new keys work, revoke old keys in Stripe
- Delete old webhook endpoints

## Restarting Celery Services

### Via Render Dashboard
1. Go to [Render Dashboard](https://dashboard.render.com)
2. Select the worker service (`ttpro-celery` or `ttpro-celery-beat`)
3. Click **Manual Deploy** → **Clear build cache & deploy**

### Force Restart
1. Go to service settings
2. Click **Restart Service** 
3. Monitor logs for successful startup

### Monitoring Celery
Check service logs for:
- Worker: `celery@hostname ready` message
- Beat: `beat: Starting...` and periodic task logs

### Common Issues
- **Redis connection errors**: Check `REDIS_URL` environment variable
- **Database errors**: Verify `DATABASE_URL` and connection pool
- **Import errors**: Ensure all dependencies are installed
- **Task failures**: Check individual task logs and error handling

## Troubleshooting

### Authentication Issues
1. Verify Firebase credentials in Render environment
2. Check authorized domains in Firebase Console
3. Test with development tokens first
4. Review authentication logs

### CORS Errors  
1. Verify origin is in `ALLOWED_ORIGINS` list
2. Check Vercel preview domains match regex pattern
3. Test with curl: `curl -H "Origin: https://domain.com" -H "Access-Control-Request-Method: GET" -X OPTIONS api-url/api/channels`

### Database Connection Issues
1. Check `DATABASE_URL` format and credentials
2. Verify network connectivity from Render
3. Monitor connection pool usage
4. Review database logs on Render

### Background Jobs Not Processing
1. Check Redis connectivity: `redis-cli ping`
2. Verify Celery worker is running and receiving tasks
3. Check Celery beat for scheduled tasks
4. Review task error logs and retry logic
5. Clear Redis queue if corrupted: `redis-cli FLUSHALL`