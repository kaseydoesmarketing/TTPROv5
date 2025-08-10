#!/bin/bash
# TTPROv5 Deployment Verification Script

set -euo pipefail

BACKEND_URL="${1:-}"
FRONTEND_URL="${2:-https://titletesterpro.com}"

if [ -z "$BACKEND_URL" ]; then
    echo "❌ Error: Please provide backend URL"
    echo "Usage: $0 https://your-backend.onrender.com [frontend-url]"
    exit 1
fi

echo "🧪 TTPROv5 DEPLOYMENT VERIFICATION"
echo "=================================="
echo "Backend: $BACKEND_URL"
echo "Frontend: $FRONTEND_URL"
echo ""

PASS_COUNT=0
FAIL_COUNT=0

check_endpoint() {
    local name="$1"
    local url="$2"
    local expected_status="$3"
    
    echo -n "Testing $name... "
    
    local status
    status=$(curl -s -w "%{http_code}" -o /dev/null "$url" 2>/dev/null || echo "000")
    
    if [[ "$expected_status" == *"$status"* ]]; then
        echo "✅ PASS ($status)"
        ((PASS_COUNT++))
    else
        echo "❌ FAIL ($status, expected $expected_status)"
        ((FAIL_COUNT++))
    fi
}

check_cors() {
    local name="$1"
    local url="$2"
    
    echo -n "Testing $name CORS... "
    
    local cors_headers
    cors_headers=$(curl -s -i -X OPTIONS "$url" \
        -H "Origin: $FRONTEND_URL" \
        -H "Access-Control-Request-Method: POST" \
        -H "Access-Control-Request-Headers: Content-Type,Authorization" 2>/dev/null | \
        grep -i "access-control-allow" || echo "")
    
    if [[ "$cors_headers" == *"access-control-allow-origin"* ]]; then
        echo "✅ PASS"
        ((PASS_COUNT++))
    else
        echo "❌ FAIL (no CORS headers)"
        ((FAIL_COUNT++))
    fi
}

check_json_response() {
    local name="$1"
    local url="$2"
    local expected_field="$3"
    
    echo -n "Testing $name... "
    
    local response
    response=$(curl -s "$url" 2>/dev/null || echo "{}")
    
    if echo "$response" | jq -e ".$expected_field" >/dev/null 2>&1; then
        echo "✅ PASS"
        ((PASS_COUNT++))
    else
        echo "❌ FAIL (missing $expected_field)"
        ((FAIL_COUNT++))
    fi
}

echo "🔍 1. BASIC HEALTH CHECKS"
echo "========================="
check_endpoint "Healthz" "$BACKEND_URL/healthz" "200"
check_json_response "Health" "$BACKEND_URL/health" "status"

echo ""
echo "🔍 2. FIREBASE DEBUG CHECK (should work if DEBUG=1)"
echo "=================================================="
check_json_response "Firebase Debug" "$BACKEND_URL/debug/firebase" "configuration_method"

echo ""
echo "🔍 3. CORS PREFLIGHT TESTS"
echo "=========================="
check_cors "Auth endpoint" "$BACKEND_URL/api/auth/firebase"
check_cors "Channels endpoint" "$BACKEND_URL/api/channels"

echo ""
echo "🔍 4. AUTHENTICATION PROTECTION"
echo "==============================="
check_endpoint "Auth without token" "$BACKEND_URL/api/auth/firebase" "401"
check_endpoint "Protected AB tests" "$BACKEND_URL/api/ab-tests" "401 307"
check_endpoint "Protected channels" "$BACKEND_URL/api/channels" "401 307"

echo ""
echo "🔍 5. FRONTEND ACCESSIBILITY"
echo "============================"
check_endpoint "Frontend root" "$FRONTEND_URL" "200"
check_endpoint "Frontend app" "$FRONTEND_URL/app" "200"

echo ""
echo "📊 VERIFICATION SUMMARY"
echo "======================="
echo "✅ Passed: $PASS_COUNT"
echo "❌ Failed: $FAIL_COUNT"
echo "📈 Success Rate: $(( PASS_COUNT * 100 / (PASS_COUNT + FAIL_COUNT) ))%"

if [ $FAIL_COUNT -eq 0 ]; then
    echo ""
    echo "🎉 ALL TESTS PASSED - DEPLOYMENT READY!"
    exit 0
else
    echo ""
    echo "⚠️  Some tests failed. Please check the configuration."
    exit 1
fi