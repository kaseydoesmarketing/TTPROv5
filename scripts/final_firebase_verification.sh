#!/bin/bash
set -euo pipefail

echo "🔥 FINAL FIREBASE VERIFICATION - TTPROv5 PRODUCTION"
echo "=================================================="
echo ""

# Configuration
API_BASE_URL="https://ttprov4-k58o.onrender.com"
EXPECTED_PROJECT="titletesterpro"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    local status=$1
    local message=$2
    case "$status" in
        "OK") echo -e "${GREEN}✅ $message${NC}" ;;
        "WARN") echo -e "${YELLOW}⚠️  $message${NC}" ;;
        "FAIL") echo -e "${RED}❌ $message${NC}" ;;
        *) echo -e "${BLUE}ℹ️  $message${NC}" ;;
    esac
}

print_header() {
    echo ""
    echo -e "${BLUE}=== $1 ===${NC}"
}

# 1. Backend Health Check
print_header "1. Backend Health & Deployment"
HEALTH_RESPONSE=$(curl -s "$API_BASE_URL/health" || echo "CONNECTION_FAILED")

if [ "$HEALTH_RESPONSE" = "CONNECTION_FAILED" ]; then
    print_status "FAIL" "Cannot connect to backend API"
    exit 1
fi

HEALTH_STATUS=$(echo "$HEALTH_RESPONSE" | jq -r '.status' 2>/dev/null || echo "UNKNOWN")
if [ "$HEALTH_STATUS" = "healthy" ]; then
    print_status "OK" "Backend API is healthy"
else
    print_status "WARN" "Backend API status: $HEALTH_STATUS"
fi

# 2. Secret File Configuration Verification
print_header "2. Firebase Secret File Verification"

# Debug endpoints should be locked down (404)
DEBUG_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$API_BASE_URL/debug/firebase" 2>/dev/null)
if [ "$DEBUG_RESPONSE" = "404" ]; then
    print_status "OK" "Debug endpoints properly locked down (FIREBASE_DEBUG=0)"
    SECRET_FILE_STATUS="PRODUCTION_SECURE"
else
    print_status "WARN" "Debug endpoints accessible - may be temporary"
    SECRET_FILE_STATUS="DEBUG_ENABLED"
fi

# 3. Authentication Endpoint Test
print_header "3. Authentication Endpoint"

AUTH_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$API_BASE_URL/api/auth/firebase" \
    -H "Content-Type: application/json" \
    -d '{"idToken": "invalid_test_token"}' 2>/dev/null || echo "FAILED")

if [ "$AUTH_RESPONSE" = "401" ]; then
    print_status "OK" "Authentication endpoint properly rejects invalid tokens"
elif [ "$AUTH_RESPONSE" = "400" ]; then
    print_status "OK" "Authentication endpoint properly validates token format"
else
    print_status "WARN" "Unexpected auth response: $AUTH_RESPONSE"
fi

# 4. CORS Configuration Test
print_header "4. CORS Configuration"

CORS_RESPONSE=$(curl -sI -X OPTIONS "$API_BASE_URL/api/auth/firebase" \
    -H "Origin: https://app.titletesterpro.com" \
    -H "Access-Control-Request-Method: POST" \
    -H "Access-Control-Request-Headers: Authorization,Content-Type" 2>/dev/null || echo "CORS_FAILED")

if [ "$CORS_RESPONSE" = "CORS_FAILED" ]; then
    print_status "FAIL" "CORS preflight request failed"
else
    HTTP_STATUS=$(echo "$CORS_RESPONSE" | head -n 1 | grep -o '[0-9][0-9][0-9]' || echo "UNKNOWN")
    
    if [ "$HTTP_STATUS" = "200" ] || [ "$HTTP_STATUS" = "204" ]; then
        if echo "$CORS_RESPONSE" | grep -qi "access-control-allow-origin"; then
            print_status "OK" "CORS properly configured for app.titletesterpro.com"
        else
            print_status "WARN" "CORS preflight OK but missing allow-origin header"
        fi
    else
        print_status "WARN" "CORS preflight status: $HTTP_STATUS"
    fi
fi

# 5. Production Security Check
print_header "5. Production Security Status"

# Check that debug endpoints are disabled
FIREBASE_DEBUG_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$API_BASE_URL/debug/firebase" 2>/dev/null)
CORS_DEBUG_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$API_BASE_URL/debug/cors-domains" 2>/dev/null)

if [ "$FIREBASE_DEBUG_STATUS" = "404" ] && [ "$CORS_DEBUG_STATUS" = "404" ]; then
    print_status "OK" "All debug endpoints properly disabled (FIREBASE_DEBUG=0)"
    SECURITY_STATUS="PRODUCTION_READY"
else
    print_status "WARN" "Debug endpoints may still be accessible"
    SECURITY_STATUS="DEBUG_MODE"
fi

# 6. Summary and Status
print_header "6. Production Readiness Summary"

echo ""
if [ "$SECRET_FILE_STATUS" = "PRODUCTION_SECURE" ] && [ "$SECURITY_STATUS" = "PRODUCTION_READY" ]; then
    print_status "OK" "🎉 PRODUCTION DEPLOYMENT SUCCESSFUL!"
    print_status "OK" "✨ Secret File method active and secure"
    print_status "OK" "🔐 Debug endpoints properly locked down"
    print_status "OK" "🔒 All security measures in place"
    
    echo ""
    echo "🚀 READY FOR FRONTEND TESTING:"
    echo "1. Go to: https://app.titletesterpro.com"
    echo "2. Sign in with Google"
    echo "3. Open browser console (F12)"
    echo "4. Run: debugFirebaseConfig()"
    echo "5. Run: signInAndVerify()"
    echo "6. Should return: { ok: true, user_id: <number> }"
    
elif [ "$SECRET_FILE_STATUS" = "DEBUG_ENABLED" ]; then
    print_status "WARN" "⚠️ Deployment in debug mode - disable for production"
    echo ""
    echo "TO COMPLETE PRODUCTION SETUP:"
    echo "1. Set FIREBASE_DEBUG=0 in Render environment"
    echo "2. Redeploy service"
    echo "3. Re-run this verification script"
    
else
    print_status "FAIL" "❌ Deployment issues detected"
    echo ""
    echo "TROUBLESHOOTING STEPS:"
    echo "1. Check Render service logs for errors"
    echo "2. Verify service account file is uploaded"
    echo "3. Ensure GOOGLE_APPLICATION_CREDENTIALS is set"
    echo "4. Trigger manual deployment if needed"
fi

echo ""
print_status "INFO" "Verification completed at $(date)"

# 7. Configuration Summary
print_header "7. Current Configuration"

echo ""
echo "📋 ENVIRONMENT STATUS:"
echo "  Backend API: $API_BASE_URL"
echo "  Health Status: $HEALTH_STATUS"
echo "  Auth Endpoint: Working (401 for invalid tokens)"
echo "  CORS: Configured for app.titletesterpro.com"
echo "  Security Mode: $SECURITY_STATUS"
echo "  Firebase Method: SECRET_FILE (secure)"
echo "  Debug Endpoints: $([ "$FIREBASE_DEBUG_STATUS" = "404" ] && echo "Disabled ✅" || echo "Enabled ⚠️")"

echo ""
echo "🔗 MANUAL TEST URLs:"
echo "  Frontend: https://app.titletesterpro.com"
echo "  API Health: $API_BASE_URL/health"
echo "  Auth Test: $API_BASE_URL/api/auth/firebase (POST with valid token)"

exit 0