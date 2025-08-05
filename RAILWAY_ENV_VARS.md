# Railway Environment Variables Required

Copy these to Railway → Your Service → Variables:

## Database
```
DATABASE_URL=postgresql://username:password@host:port/database
REDIS_URL=redis://username:password@host:port
```

## Authentication & APIs
```
SECRET_KEY=your-secret-key-here
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret
YOUTUBE_API_KEY=your-youtube-api-key
```

## Firebase
```
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_PRIVATE_KEY=-----BEGIN PRIVATE KEY-----\nyour-private-key\n-----END PRIVATE KEY-----
FIREBASE_PRIVATE_KEY_ID=your-private-key-id
FIREBASE_CLIENT_EMAIL=firebase-adminsdk-xxx@your-project.iam.gserviceaccount.com
FIREBASE_CLIENT_ID=your-client-id
```

## Optional (Stripe)
```
STRIPE_SECRET_KEY=sk_test_or_live_xxx
STRIPE_PUBLISHABLE_KEY=pk_test_or_live_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx
```

## System
```
ENVIRONMENT=production
CORS_ORIGINS=https://www.titletesterpro.com,https://titletesterpro.com
```

## Railway Specific
```
PORT=8000
```