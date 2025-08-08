# TTPROv5 Production Acceptance Tests

## Deployment Status
- **Branch**: `bootstrap/v5`
- **Commit**: `08127bbe` (post-merge conflict resolution)
- **Release**: v5.0.0

## Core Configuration Verification

### CORS Configuration (Deterministic)
```python
# app/main.py lines 88-103
from starlette.middleware.cors import CORSMiddleware

ALLOWED_ORIGINS = [
    "https://www.titletesterpro.com",
    "https://titletesterpro.com", 
    "http://localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_origin_regex=r"^https://.*ttpro[-]?(ov4|ov5|v5)?.*vercel\.app$",
    allow_credentials=True,
    allow_methods=["GET","POST","PUT","PATCH","DELETE","OPTIONS"],
    allow_headers=["Authorization","Content-Type","X-Requested-With","Accept"],
    expose_headers=["Content-Type","Content-Length"]
)
```

### Render Services Configuration
```yaml
# render.yaml
services:
  - type: web
    name: ttpro-api
    env: docker
    autoDeploy: true
    healthCheckPath: /
    preDeployCommand: alembic upgrade head
  - type: worker  
    name: ttpro-celery
    startCommand: celery -A app.robust_tasks worker --loglevel=info
  - type: worker
    name: ttpro-celery-beat  
    startCommand: celery -A app.robust_tasks beat --loglevel=info --pidfile=
```

### Environment Variables Required
- `DATABASE_URL` (Render PostgreSQL)
- `REDIS_URL` (External Redis)
- `ENVIRONMENT=production`
- `FIREBASE_PROJECT_ID`
- `FIREBASE_CLIENT_EMAIL`
- `FIREBASE_PRIVATE_KEY`
- `YOUTUBE_API_KEY`
- `OPENAI_API_KEY`
- `STRIPE_SECRET_KEY`
- `STRIPE_PRICE_ID`
- `STRIPE_WEBHOOK_SECRET`

### Database Migration
- **Migration File**: `alembic/versions/add_stripe_fields_20250808.py`
- **Stripe Fields Added**: `stripe_customer_id`, `stripe_subscription_id`, `subscription_status`, `subscription_plan`, `subscription_period_end`, `subscription_end_date`, `subscription_updated_at`, `last_payment_date`, `last_payment_amount`

### Stripe Webhook Configuration
- **Endpoint**: `/api/billing/webhook`
- **Required Events**:
  - `customer.subscription.created`
  - `customer.subscription.updated`
  - `customer.subscription.deleted`
  - `invoice.payment_succeeded`
  - `invoice.payment_failed`
  - `checkout.session.completed`

## Smoke Test Results
Run with: `./scripts/smoke.sh <API_URL> https://www.titletesterpro.com`

Expected Results:
- ✅ CORS preflight responses include `Access-Control-Allow-Origin`
- ✅ `/health` returns `{"status": "healthy"}`
- ✅ Protected endpoints (`/api/ab-tests`, `/api/channels`) return `401`
- ✅ Webhook endpoint (`/api/billing/webhook`) returns `400/401` without signature

## Marketing Site
- **Framework**: Next.js 14.2.31
- **Build**: ✅ Successful
- **Deployment Target**: Vercel
- **Root Directory**: `/marketing`
- **Environment**: `NEXT_PUBLIC_APP_URL=https://app.titletesterpro.com`

## Manual Verification Checklist
- [ ] Render API service deployed and healthy
- [ ] Celery worker and beat services running
- [ ] Database migrations applied successfully
- [ ] Stripe webhook endpoint created and secret configured
- [ ] Marketing site deployed on Vercel
- [ ] CORS working between marketing and API
- [ ] Authentication flow functional
- [ ] A/B testing features accessible

## Rollback Plan
1. **Render Rollback**: Dashboard → Service → Deployments → Previous build
2. **Database Rollback**: `alembic downgrade -1` (if needed)
3. **Webhook Disable**: Stripe Dashboard → Webhooks → Disable endpoint
4. **Emergency Contact**: Check service logs in Render dashboard

## CI/CD Status
- **Backend Workflow**: `.github/workflows/backend.yml` 
- **Frontend Workflow**: `.github/workflows/frontend.yml`
- **Smoke Tests**: `scripts/smoke.sh`
EOF < /dev/null