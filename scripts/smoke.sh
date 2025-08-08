#!/usr/bin/env bash
set -euo pipefail
API="${1:-https://ttprov4-k58o.onrender.com}"
ORIGIN="${2:-https://www.titletesterpro.com}"

echo "== CORS preflights =="
curl -sS -I -X OPTIONS "$API/api/channels" \
  -H "Origin: $ORIGIN" -H "Access-Control-Request-Method: GET" \
  | grep -i access-control-allow-origin

echo "== Health ==" && curl -sS "$API/health" | jq -r .status

echo "== Auth unauth 401 expected ==" && curl -sS -i "$API/api/ab-tests" | head -n 1