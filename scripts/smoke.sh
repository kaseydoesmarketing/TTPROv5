#!/usr/bin/env bash
set -euo pipefail
<<<<<<< HEAD
API="${1:-https://ttprov4-k58o.onrender.com}"
ORIGIN="${2:-https://www.titletesterpro.com}"

echo "== CORS preflights =="
curl -sS -i -X OPTIONS "$API/api/channels" \
  -H "Origin: $ORIGIN" -H "Access-Control-Request-Method: GET" | sed -n '1,/^$/p'

echo "== Health =="
curl -sS "$API/health" | jq -r .status || true

echo "== Unauth /api/ab-tests (expect 401) =="
curl -sS -i "$API/api/ab-tests" | head -n 1
=======

API="${1:-https://ttprov4-k58o.onrender.com}"
ORIGIN="${2:-https://www.titletesterpro.com}"

echo "🔍 Running smoke tests against: $API"
echo "🌐 Using origin: $ORIGIN"
echo

# Test CORS preflight
echo "== CORS preflights =="
echo "Testing OPTIONS /api/channels with Origin: $ORIGIN"
curl -sS -i -X OPTIONS "$API/api/channels" \
  -H "Origin: $ORIGIN" \
  -H "Access-Control-Request-Method: GET" \
  -H "Access-Control-Request-Headers: Authorization,Content-Type" \
  | sed -n '1,/^$/p'

echo
echo "Testing OPTIONS /api/ab-tests with Origin: $ORIGIN"  
curl -sS -i -X OPTIONS "$API/api/ab-tests" \
  -H "Origin: $ORIGIN" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Authorization,Content-Type" \
  | sed -n '1,/^$/p'

echo
echo "== Health checks =="
echo "Testing GET /health"
curl -sS "$API/health" | jq -r '.status // "No status field"' || echo "Health check failed or no JSON response"

echo
echo "Testing GET /"
curl -sS "$API/" | jq -r '.status // "No status field"' || echo "Root health check failed or no JSON response"

echo
echo "== Authentication checks =="
echo "Testing GET /api/ab-tests (expect 401 unauthorized)"
HTTP_STATUS=$(curl -sS -o /dev/null -w "%{http_code}" "$API/api/ab-tests")
if [ "$HTTP_STATUS" = "401" ]; then
    echo "✅ Correctly returns 401 for unauthorized access"
else
    echo "❌ Expected 401 but got $HTTP_STATUS"
fi

echo
echo "Testing GET /api/channels (expect 401 unauthorized)"
HTTP_STATUS=$(curl -sS -o /dev/null -w "%{http_code}" "$API/api/channels")  
if [ "$HTTP_STATUS" = "401" ]; then
    echo "✅ Correctly returns 401 for unauthorized access"
else
    echo "❌ Expected 401 but got $HTTP_STATUS"
fi

echo
echo "== Stripe webhook endpoint =="
echo "Testing POST /api/billing/webhook (expect 400 bad request - no signature)"
HTTP_STATUS=$(curl -sS -o /dev/null -w "%{http_code}" -X POST "$API/api/billing/webhook" \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}')
if [ "$HTTP_STATUS" = "400" ] || [ "$HTTP_STATUS" = "401" ]; then
    echo "✅ Webhook endpoint responding (got $HTTP_STATUS as expected)"
else
    echo "❌ Unexpected webhook response: $HTTP_STATUS"
fi

echo
echo "🎯 Smoke test completed!"
echo "📋 Expected results:"
echo "  - CORS headers: access-control-allow-origin, access-control-allow-methods"
echo "  - Health endpoints: return status 'healthy' or 'ok'"
echo "  - Protected endpoints: return 401 when unauthorized"
echo "  - Webhook endpoint: return 400/401 without proper Stripe signature"
>>>>>>> ci/smoke-and-build
