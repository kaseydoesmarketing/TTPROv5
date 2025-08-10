#!/bin/bash
set -euo pipefail

echo "🔧 TTPROv5 Backend Connectivity Fix Script"
echo "=========================================="
echo ""

# Backend URL from configuration
BACKEND_URL="https://ttprov4-k58o.onrender.com"
FRONTEND_MARKETING_URL=""
RENDER_SERVICE_ID="srv-d29srkqdbo4c73antk40"  # From previous deployment logs

echo "Current Backend URL: $BACKEND_URL"
echo ""

# Step 1: Test current backend status
echo "📋 STEP 1: Testing Current Backend Status"
echo "-----------------------------------------"

echo "Testing root endpoint..."
ROOT_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$BACKEND_URL/" 2>/dev/null || echo "000")
echo "GET $BACKEND_URL/ -> $ROOT_STATUS"

echo "Testing health endpoint..."
HEALTH_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$BACKEND_URL/health" 2>/dev/null || echo "000")
echo "GET $BACKEND_URL/health -> $HEALTH_STATUS"

if [ "$ROOT_STATUS" = "404" ] && [ "$HEALTH_STATUS" = "404" ]; then
    echo "❌ Backend service is not running (404 with 'no-server' error)"
    echo "   This indicates the Render service is not started properly"
    echo ""
else
    echo "✅ Backend appears to be responding"
    echo ""
    exit 0
fi

# Step 2: Check for alternative service URLs
echo "📋 STEP 2: Checking for Alternative Service URLs"
echo "-----------------------------------------------"

# Test if there's a new service with a different URL pattern
ALTERNATIVE_URLS=(
    "https://ttprov5-api.onrender.com"
    "https://titletesterpro-api.onrender.com" 
    "https://ttpro-backend.onrender.com"
    "https://ttprov4.onrender.com"
)

WORKING_URL=""
for url in "${ALTERNATIVE_URLS[@]}"; do
    echo "Testing $url..."
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$url/" 2>/dev/null || echo "000")
    if [ "$STATUS" = "200" ]; then
        echo "✅ Found working backend at: $url"
        WORKING_URL=$url
        break
    elif [ "$STATUS" != "404" ]; then
        echo "⚠️  $url responds with status $STATUS"
    else
        echo "❌ $url not available"
    fi
done

echo ""

if [ -n "$WORKING_URL" ]; then
    echo "🎉 SOLUTION FOUND: Working backend at $WORKING_URL"
    echo ""
    echo "Next steps to update frontend configuration:"
    echo "1. Update Vercel environment variables:"
    echo "   - NEXT_PUBLIC_API_BASE_URL=$WORKING_URL"
    echo ""
    echo "2. Update marketing/lib/api.ts if needed"
    echo "3. Update marketing/vercel.json proxy rules"
    echo ""
    exit 0
fi

# Step 3: Provide manual intervention steps
echo "📋 STEP 3: Manual Intervention Required"
echo "---------------------------------------"

echo "No working backend service found. The Render service needs to be restarted or reconfigured."
echo ""
echo "IMMEDIATE ACTION REQUIRED:"
echo ""
echo "1. 🔍 CHECK RENDER DASHBOARD:"
echo "   - Go to: https://dashboard.render.com"
echo "   - Find service: ttpro-api (ID: $RENDER_SERVICE_ID)"
echo "   - Check service logs for startup errors"
echo ""
echo "2. 🔄 LIKELY ISSUES TO CHECK:"
echo "   a) Environment Variables Missing:"
echo "      - DATABASE_URL (PostgreSQL connection)"
echo "      - FIREBASE_PROJECT_ID, GOOGLE_APPLICATION_CREDENTIALS"
echo "      - GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET"
echo "      - JWT_SECRET_KEY"
echo ""
echo "   b) Database Service Not Running:"
echo "      - PostgreSQL service may be down"
echo "      - Connection string may be incorrect"
echo ""
echo "   c) Branch/Deployment Issues:"
echo "      - Service may be deploying from wrong branch"
echo "      - Build may be failing during startup"
echo ""
echo "3. 🛠️ QUICK FIXES TO TRY:"
echo "   a) Manual Deploy:"
echo "      - Go to Render dashboard"
echo "      - Click 'Manual Deploy' on ttpro-api service"
echo ""
echo "   b) Check Service Logs:"
echo "      - Look for startup errors"
echo "      - Check for database connection failures"
echo "      - Verify environment variable issues"
echo ""
echo "   c) Verify Environment Variables:"
echo "      - Ensure all critical variables are set"
echo "      - Check for typos in variable names"
echo ""
echo "4. 🔧 NUCLEAR OPTION - Deploy New Service:"
echo "   - Create new Render service from TTPROv5 repo"
echo "   - Use branch: bootstrap/v5"
echo "   - Configure all environment variables"
echo "   - Update frontend to use new backend URL"
echo ""
echo "5. 📞 NEED HELP?"
echo "   The service configuration is in /Users/kvimedia/TTPROv5/render.yaml"
echo "   FastAPI app entry point: /Users/kvimedia/TTPROv5/app/main.py"
echo "   Docker configuration: /Users/kvimedia/TTPROv5/Dockerfile"
echo ""
echo "Once the backend is fixed, test with:"
echo "curl https://YOUR-BACKEND-URL.onrender.com/health"
echo ""
echo "Expected response:"
echo '{"status":"healthy","timestamp":"...","service":"titletesterpro-api"}'

echo ""
echo "🚨 SUMMARY: Backend service at $BACKEND_URL is not running"
echo "   Check Render dashboard and restart the service with proper configuration"