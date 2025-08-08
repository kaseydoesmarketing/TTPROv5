# TTPROv5 Acceptance Checklist
## API (Render)
- [ ] /health responds OK
- [ ] CORS headers allow titletesterpro.com + Vercel previews
- [ ] /api/ab-tests and /api/channels return 401 when unauthenticated
- [ ] /api/billing/webhook returns 400/401 without Stripe signature
- [ ] Alembic migrations applied automatically on deploy

## Workers
- [ ] Celery worker and beat are running (logs show connected to REDIS_URL)

## Marketing (Vercel)
- [ ] Deployed from /marketing
- [ ] Uses NEXT_PUBLIC_APP_URL to point to app

## DNS
- [ ] titletesterpro.com and www -> Vercel (marketing)
- [ ] app.titletesterpro.com (or chosen app host) -> Render API

## Smoke Test
Run:
`./scripts/smoke.sh https://YOUR-RENDER-URL.onrender.com https://www.titletesterpro.com`
Expect CORS on OPTIONS, 401 for protected routes, 400/401 for webhook.
DOC < /dev/null