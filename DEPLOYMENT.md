# Deployment Configuration

## Required Environment Variables

### Render (API)

The following environment variables must be set in the Render dashboard for the API service:

- `DATABASE_URL` - PostgreSQL connection string (automatically provided by Render)
- `REDIS_URL` - Redis connection string for Celery tasks
- `STRIPE_SECRET_KEY` - Stripe secret key for payment processing
- `STRIPE_WEBHOOK_SECRET` - Stripe webhook endpoint secret
- `FIREBASE_PROJECT_ID` - Firebase project identifier
- `FIREBASE_PRIVATE_KEY_ID` - Firebase service account private key ID
- `FIREBASE_PRIVATE_KEY` - Firebase service account private key (full PEM format)
- `FIREBASE_CLIENT_EMAIL` - Firebase service account email
- `FIREBASE_CLIENT_ID` - Firebase service account client ID
- `YOUTUBE_API_KEY` - YouTube Data API v3 key
- `GOOGLE_CLIENT_ID` - Google OAuth client ID
- `GOOGLE_CLIENT_SECRET` - Google OAuth client secret

### Vercel (Frontend)

Set these environment variables for both Preview and Production environments in Vercel:

- `VITE_API_URL` - Backend API URL (e.g., `https://ttprov4-k58o.onrender.com` or `https://api.titletesterpro.com`)
- `VITE_FIREBASE_API_KEY` - Firebase Web API key
- `VITE_FIREBASE_AUTH_DOMAIN` - `titletesterpro.firebaseapp.com`
- `VITE_FIREBASE_PROJECT_ID` - `titletesterpro`
- `VITE_FIREBASE_STORAGE_BUCKET` - `titletesterpro.appspot.com`
- `VITE_FIREBASE_MESSAGING_SENDER_ID` - `618794070994`
- `VITE_FIREBASE_APP_ID` - `1:618794070994:web:154fb461d986c434eece0b`
- `VITE_FIREBASE_MEASUREMENT_ID` - `G-CP6NQXEEW6`

### Firebase Configuration

In Firebase Console → Authentication → Settings → Authorized Domains, add:

- `titletesterpro.com`
- `www.titletesterpro.com`
- Your Vercel preview domains (e.g., `*.vercel.app`)

## Service Dependencies

### Required Services

1. **PostgreSQL Database** - Primary data storage
2. **Redis** - Background job queue for Celery
3. **Stripe** - Payment processing
4. **Firebase** - Authentication
5. **YouTube API** - Channel and video management

### Optional Services

- **Monitoring** - Sentry or similar for error tracking
- **Analytics** - Google Analytics or similar

## Deployment Order

1. Set up database and Redis on Render
2. Configure all environment variables
3. Deploy backend API
4. Configure Firebase authorized domains
5. Deploy frontend on Vercel
6. Set up Stripe webhooks
7. Test smoke endpoints

## Health Check Endpoints

- `/` - Basic health check
- `/health` - Detailed health status
- `/health/environment` - Environment configuration status
- `/health/database` - Database connection status

## Webhook Configuration

### Stripe Webhook

After deployment, configure Stripe webhook endpoint:

1. Go to Stripe Dashboard → Webhooks
2. Add endpoint: `https://<api-domain>/api/billing/webhook`
3. Select events:
   - `checkout.session.completed`
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`
4. Copy the webhook secret and set as `STRIPE_WEBHOOK_SECRET`

## Troubleshooting

### Common Issues

1. **CORS Errors**: Ensure your domain is included in the CORS configuration
2. **Auth Failures**: Verify Firebase credentials and authorized domains
3. **Database Connection**: Check DATABASE_URL format and network access
4. **Background Jobs Not Running**: Verify Redis connection and Celery workers are running

### Logs

- Render: Check service logs in Render dashboard
- Vercel: Check function logs in Vercel dashboard
- Firebase: Check Authentication logs in Firebase Console