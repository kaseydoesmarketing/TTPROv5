#\!/usr/bin/env bash
set -euo pipefail
API="${1:-https://RENDER_API_URL_HERE}"
ORIGIN="${2:-https://www.titletesterpro.com}"
echo "🔍 Smoke tests for $API (Origin: $ORIGIN)"

echo "== CORS preflight /api/channels =="
curl -sS -i -X OPTIONS "$API/api/channels" \
  -H "Origin: $ORIGIN" \
  -H "Access-Control-Request-Method: GET" \
  -H "Access-Control-Request-Headers: Authorization,Content-Type" \
  | sed -n '1,/^$/p'
echo

echo "== Health =="
curl -sS "$API/health" || true
echo
curl -sS "$API/" || true
echo

echo "== Auth (401 expected) =="
code=$(curl -sS -o /dev/null -w "%{http_code}" "$API/api/ab-tests")
echo "/api/ab-tests -> $code (expect 401)"
code=$(curl -sS -o /dev/null -w "%{http_code}" "$API/api/channels")
echo "/api/channels -> $code (expect 401)"
echo

echo "== Stripe webhook (400/401 expected) =="
code=$(curl -sS -o /dev/null -w "%{http_code}" -X POST "$API/api/billing/webhook" \
  -H "Content-Type: application/json" -d '{"test":true}')
echo "/api/billing/webhook -> $code (expect 400/401)"
echo "🎯 Smoke test complete"
