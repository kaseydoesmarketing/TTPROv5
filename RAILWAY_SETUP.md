# Railway Deployment Setup Guide

## Prerequisites
You need to provision the following services in Railway:

### 1. PostgreSQL Database
- Go to Railway Dashboard
- Click "New" → "Database" → "PostgreSQL"
- Railway will automatically provide `DATABASE_URL` environment variable

### 2. Redis
- Click "New" → "Database" → "Redis"  
- Railway will automatically provide `REDIS_URL` environment variable

## Required Environment Variables

After provisioning PostgreSQL and Redis, add these environment variables in Railway:

### Firebase Configuration (Required)
```
FIREBASE_PROJECT_ID=your-firebase-project-id
FIREBASE_PRIVATE_KEY=your-firebase-private-key
FIREBASE_PRIVATE_KEY_ID=your-firebase-key-id
FIREBASE_CLIENT_EMAIL=your-firebase-client-email
FIREBASE_CLIENT_ID=your-firebase-client-id
```

### Google OAuth (Required)
```
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

### YouTube API (Required)
```
YOUTUBE_API_KEY=your-youtube-api-key
```

### Application Security (Required)
```
SECRET_KEY=your-secret-key-here-make-it-long-and-random
```

### Stripe (Optional)
```
STRIPE_SECRET_KEY=your-stripe-secret-key
STRIPE_PUBLISHABLE_KEY=your-stripe-publishable-key
STRIPE_WEBHOOK_SECRET=your-stripe-webhook-secret
```

### CORS Configuration (Optional - has default)
```
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### Environment (Optional - defaults to production)
```
ENVIRONMENT=production
```

## Deployment Steps

1. **Fork/Clone Repository**
   - Connect your GitHub repository to Railway

2. **Create Services**
   - Add PostgreSQL service
   - Add Redis service
   - Both will automatically inject their URLs

3. **Configure Environment Variables**
   - Go to your app service settings
   - Add all required environment variables listed above

4. **Deploy**
   - Railway will automatically:
     - Build using `railway.dockerfile`
     - Run database migrations (`alembic upgrade head`)
     - Start the application with `start.sh`

5. **Health Check**
   - Visit `https://your-app.railway.app/health`
   - Should return status "operational" when fully configured

## Troubleshooting

### Database Connection Issues
- Ensure PostgreSQL service is running
- Check that `DATABASE_URL` is properly set
- Look at deployment logs for connection errors

### Redis Connection Issues  
- Ensure Redis service is running
- Check that `REDIS_URL` is properly set
- App will work without Redis but with reduced performance

### Missing Environment Variables
- Check `/health` endpoint for detailed status
- Look for "emergency mode" warnings in logs
- Ensure all critical variables are set

### Port Issues
- Railway automatically sets `PORT` environment variable
- The app is configured to use this automatically
- Don't hardcode port 8000 in production

## Important Notes

1. **Database Migrations**: Run automatically on deploy via `preDeployCommand`
2. **Health Checks**: Railway monitors `/health` endpoint
3. **Restart Policy**: Set to "on_failure" for automatic recovery
4. **SQLite Fallback**: Only for local development, not for production