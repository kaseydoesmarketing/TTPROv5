#!/usr/bin/env bash
set -euo pipefail
API="${1:-https://ttprov4-k58o.onrender.com}"
ORIGIN="${2:-https://www.titletesterpro.com}"

echo "== CORS preflights =="
curl -sS -i -X OPTIONS "$API/api/channels" \
  -H "Origin: $ORIGIN" -H "Access-Control-Request-Method: GET" | sed -n '1,/^$/p'

echo "== Health =="
curl -sS "$API/health" | jq -r .status || true

echo "== Unauth /api/ab-tests (expect 401) =="
curl -sS -i "$API/api/ab-tests" | head -n 1