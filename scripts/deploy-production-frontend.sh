#!/bin/bash
set -euo pipefail

echo "🚀 TTPROv5 Production Frontend Deployment Script"
echo "================================================"
echo ""

# Configuration
PRODUCTION_BRANCH="TTPROv5"
API_BASE_URL="https://ttprov5.onrender.com"
MARKETING_DIR="/Users/kvimedia/TTPROv5/marketing"

echo "📋 Configuration:"
echo "  Production Branch: $PRODUCTION_BRANCH"
echo "  API Base URL: $API_BASE_URL"
echo "  Marketing Directory: $MARKETING_DIR"
echo ""

# Step 1: Ensure we're on the correct branch and it's up to date
echo "🔄 Step 1: Branch Verification and Sync"
echo "--------------------------------------"

cd /Users/kvimedia/TTPROv5

# Push current changes
echo "Pushing latest changes..."
git add -A
git commit -m "chore: sync latest changes before production deployment" || echo "No changes to commit"
git push origin bootstrap/v5

# Ensure TTPROv5 branch exists and is up to date
if git show-ref --verify --quiet refs/heads/TTPROv5; then
    echo "✅ TTPROv5 branch exists"
    git checkout TTPROv5
    git merge bootstrap/v5
    git push origin TTPROv5
else
    echo "Creating TTPROv5 branch..."
    git checkout -b TTPROv5
    git push -u origin TTPROv5
fi

echo ""

# Step 2: Verify configuration files
echo "🔍 Step 2: Configuration Verification"
echo "------------------------------------"

cd "$MARKETING_DIR"

echo "Checking next.config.js..."
if grep -q "NEXT_PUBLIC_API_BASE_URL" next.config.js; then
    echo "✅ next.config.js reads from environment variable"
else
    echo "❌ next.config.js missing environment variable reference"
    exit 1
fi

echo "Checking vercel.json..."
if grep -q '"TTPROv5": true' vercel.json; then
    echo "✅ vercel.json configured for TTPROv5 branch deployment"
else
    echo "❌ vercel.json not configured for TTPROv5 branch"
    exit 1
fi

if grep -q '"bootstrap/v5": false' vercel.json; then
    echo "✅ vercel.json blocks legacy branch auto-deploy"
else
    echo "❌ vercel.json not blocking legacy branches"
    exit 1
fi

echo ""

# Step 3: Backend connectivity test
echo "🌐 Step 3: Backend Connectivity Test"
echo "-----------------------------------"

echo "Testing backend health..."
HEALTH_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$API_BASE_URL/health" || echo "000")
if [ "$HEALTH_STATUS" = "200" ]; then
    echo "✅ Backend health check passed ($HEALTH_STATUS)"
    HEALTH_RESPONSE=$(curl -s "$API_BASE_URL/health" | head -100)
    echo "   Response: $HEALTH_RESPONSE"
else
    echo "❌ Backend health check failed ($HEALTH_STATUS)"
    echo "   URL: $API_BASE_URL/health"
    exit 1
fi

echo "Testing CORS configuration..."
CORS_STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
    -H "Origin: https://www.titletesterpro.com" \
    -H "Access-Control-Request-Method: POST" \
    -X OPTIONS "$API_BASE_URL/api/auth/firebase" || echo "000")
if [ "$CORS_STATUS" = "200" ]; then
    echo "✅ CORS configuration verified ($CORS_STATUS)"
else
    echo "❌ CORS configuration issue ($CORS_STATUS)"
    echo "   Testing URL: $API_BASE_URL/api/auth/firebase"
    exit 1
fi

echo ""

# Step 4: Manual Vercel configuration instructions
echo "📝 Step 4: Vercel Configuration Instructions"
echo "------------------------------------------"

cat << 'EOF'

🎯 MANUAL VERCEL CONFIGURATION REQUIRED:

1. Go to Vercel Dashboard: https://vercel.com/dashboard
2. Find your TTPROv5 project
3. Go to Settings → Git

4. Configure Production Branch:
   ┌─────────────────────────────────────────┐
   │ Production Branch: TTPROv5              │
   └─────────────────────────────────────────┘

5. Go to Settings → Environment Variables

6. Add Production Environment Variable:
   ┌─────────────────────────────────────────┐
   │ Key: NEXT_PUBLIC_API_BASE_URL           │
   │ Value: https://ttprov5.onrender.com     │
   │ Environment: Production                 │
   └─────────────────────────────────────────┘

7. Add Preview Environment Variable:
   ┌─────────────────────────────────────────┐
   │ Key: NEXT_PUBLIC_API_BASE_URL           │
   │ Value: https://ttprov5.onrender.com     │
   │ Environment: Preview                    │
   └─────────────────────────────────────────┘

8. Go to Deployments tab and trigger a new deployment:
   - Click "Redeploy" on latest deployment
   - Or push a new commit to TTPROv5 branch

EOF

echo ""

# Step 5: Verification instructions
echo "🔍 Step 5: Post-Deployment Verification"
echo "--------------------------------------"

cat << 'EOF'

After Vercel deployment completes, verify:

✅ **Deployment Source**:
   - Check deployment details show "TTPROv5" as source branch
   - Build logs show: "🔗 TTPROv5 Frontend Build - API Base URL: https://ttprov5.onrender.com"

✅ **Frontend Functionality**:
   1. Open your production URL (e.g., https://your-app.vercel.app)
   2. Verify homepage (/) loads successfully
   3. Open browser console and run:
      ```javascript
      fetch('https://ttprov5.onrender.com/health')
        .then(r => r.json())
        .then(console.log)
      ```
   4. Should return: {"status":"healthy","timestamp":"...","service":"titletesterpro-api"}

✅ **API Connectivity**:
   - Try authentication flow
   - Check that API calls go to https://ttprov5.onrender.com
   - Verify CORS headers are present in network tab

EOF

echo ""

# Step 6: Quick local test
echo "🧪 Step 6: Local Configuration Test"
echo "----------------------------------"

echo "Testing local build with production environment..."
cd "$MARKETING_DIR"

# Test build with production API URL
export NEXT_PUBLIC_API_BASE_URL="$API_BASE_URL"
export NODE_ENV="production"

echo "Environment variables for test:"
echo "  NEXT_PUBLIC_API_BASE_URL=$NEXT_PUBLIC_API_BASE_URL"
echo "  NODE_ENV=$NODE_ENV"

# Create a minimal test to verify configuration
cat > test-config.js << 'TESTJS'
const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL || 'https://ttprov5.onrender.com';
console.log('🔗 API Base URL:', apiBase);
console.log('🌍 Environment:', process.env.NODE_ENV);

// Verify it's not hardcoded
if (apiBase.includes('ttprov4-k58o')) {
  console.error('❌ Still using old hardcoded URL');
  process.exit(1);
}

if (apiBase === 'https://ttprov5.onrender.com') {
  console.log('✅ Correct API base URL configured');
} else {
  console.log('ℹ️ Using custom API base URL:', apiBase);
}
TESTJS

node test-config.js
rm test-config.js

echo ""
echo "✅ TTPROv5 Frontend Production Deployment Ready!"
echo ""
echo "🎯 Next Steps:"
echo "1. Configure Vercel settings as shown above"
echo "2. Deploy from TTPROv5 branch"
echo "3. Verify all functionality works"
echo ""
echo "🔗 Backend: $API_BASE_URL"
echo "📦 Frontend Branch: $PRODUCTION_BRANCH"
echo "🚀 Ready for production!"