# Deployment Configuration

## Required Environment Variables

### Render (API Service)

Set these environment variables in the Render dashboard:

- `DATABASE_URL` - PostgreSQL connection string (automatically provided)
- `REDIS_URL` - Redis connection string for Celery background tasks
- `STRIPE_SECRET_KEY` - Stripe secret key for payment processing
- `STRIPE_WEBHOOK_SECRET` - Stripe webhook endpoint verification secret
- `FIREBASE_PROJECT_ID` - Firebase project identifier
- `FIREBASE_PRIVATE_KEY_ID` - Firebase service account private key ID
- `FIREBASE_PRIVATE_KEY` - Firebase service account private key (full PEM format)
- `FIREBASE_CLIENT_EMAIL` - Firebase service account email address
- `FIREBASE_CLIENT_ID` - Firebase service account client ID
- `FIREBASE_AUTH_URI` - https://accounts.google.com/o/oauth2/auth
- `FIREBASE_TOKEN_URI` - https://oauth2.googleapis.com/token
- `FIREBASE_AUTH_PROVIDER_X509_CERT_URL` - https://www.googleapis.com/oauth2/v1/certs
- `YOUTUBE_API_KEY` - YouTube Data API v3 key for channel access
- `GOOGLE_CLIENT_ID` - Google OAuth client ID for authentication
- `GOOGLE_CLIENT_SECRET` - Google OAuth client secret
- `ENVIRONMENT` - Set to "production"
- `LOG_LEVEL` - Set to "INFO"

### Vercel (Frontend)

Set for both Preview and Production environments:

- `VITE_API_URL` - Backend API URL (https://your-render-api-url.com)
- `VITE_FIREBASE_API_KEY` - Firebase Web API key
- `VITE_FIREBASE_AUTH_DOMAIN` - titletesterpro.firebaseapp.com
- `VITE_FIREBASE_PROJECT_ID` - titletesterpro
- `VITE_FIREBASE_STORAGE_BUCKET` - titletesterpro.appspot.com
- `VITE_FIREBASE_MESSAGING_SENDER_ID` - 618794070994
- `VITE_FIREBASE_APP_ID` - 1:618794070994:web:154fb461d986c434eece0b
- `VITE_FIREBASE_MEASUREMENT_ID` - G-CP6NQXEEW6

### Firebase Console Configuration

In Firebase Console → Authentication → Settings → Authorized Domains, add:

- `titletesterpro.com`
- `www.titletesterpro.com`  
- `*.vercel.app` (for Vercel previews)

## Deployment Services

### Required Services
1. **PostgreSQL Database** - User data and subscriptions
2. **Redis** - Background job queue for Celery
3. **Web Service** - FastAPI application
4. **Celery Worker** - Background task processing
5. **Celery Beat** - Scheduled task management

### Service Dependencies
- Web service depends on Database and Redis
- Celery worker depends on Database and Redis
- Celery beat depends on Redis

## Health Checks

Available endpoints:
- `/` - Basic health status
- `/health` - Detailed application health
- `/healthz` - Simple OK response

## Database Migrations

Run migrations after deployment:
```bash
alembic upgrade head
```

## Webhook Configuration

After API deployment, configure Stripe webhook:
1. Go to Stripe Dashboard → Webhooks
2. Add endpoint: `https://your-api-domain.com/api/billing/webhook`
3. Select these events:
   - `checkout.session.completed`
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
4. Copy webhook signing secret to `STRIPE_WEBHOOK_SECRET`