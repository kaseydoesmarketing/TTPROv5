#!/bin/bash
# TTPROv5 Backend Deployment Helper Script

set -euo pipefail

echo "🚀 TTPROv5 BACKEND DEPLOYMENT HELPER"
echo "===================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check current branch
CURRENT_BRANCH=$(git branch --show-current)
REQUIRED_BRANCH="fix/ttprov5-backend-redeploy-20250810_121500"

if [ "$CURRENT_BRANCH" != "$REQUIRED_BRANCH" ]; then
    echo -e "${YELLOW}⚠️  Warning: Current branch is '$CURRENT_BRANCH'${NC}"
    echo -e "${YELLOW}   Required branch is '$REQUIRED_BRANCH'${NC}"
    echo ""
    read -p "Switch to required branch? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git checkout "$REQUIRED_BRANCH"
    fi
fi

# Push latest changes
echo ""
echo "📤 Pushing latest changes to GitHub..."
git push origin "$REQUIRED_BRANCH"

echo ""
echo -e "${GREEN}✅ Code is ready for deployment!${NC}"
echo ""
echo "📋 MANUAL STEPS IN RENDER DASHBOARD:"
echo "===================================="
echo ""
echo "1. Go to: https://dashboard.render.com/"
echo ""
echo "2. Click 'New +' → 'Web Service'"
echo ""
echo "3. Connect your repository:"
echo "   - Repository: TTPROv5"
echo "   - Branch: fix/ttprov5-backend-redeploy-20250810_121500"
echo ""
echo "4. Configure service:"
echo "   - Name: ttprov5-api"
echo "   - Environment: Docker"
echo "   - Instance Type: Free (or your choice)"
echo "   - Health Check Path: /"
echo ""
echo "5. Environment Variables to add:"
cat << 'EOF'
   ENVIRONMENT=production
   LOG_LEVEL=info
   APP_NAME=titletesterpro
   
   # Firebase Admin
   GOOGLE_APPLICATION_CREDENTIALS=/etc/secrets/firebase-key.json
   ALLOW_ENV_FALLBACK=0
   FIREBASE_DEBUG=1
   
   # Google OAuth
   GOOGLE_CLIENT_ID=618794070994-70oauf1olrgmqvg284mpj5u2lf75jl1q.apps.googleusercontent.com
   GOOGLE_CLIENT_SECRET=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
   GOOGLE_API_KEY=AIzaSyA8hjvKfC_D1rQqIWgjhxq-xM1cmgDB3z4
   
   # JWT Secret
   JWT_SECRET_KEY=bB9uYvA4X7cP3fN2rL6mQ8tH1jR5wK0zS5dM7pV9qT2yU8gE1cL0bF4nJ6rQ2aW7
   
   # CORS Origins
   CORS_ORIGINS=https://www.titletesterpro.com,https://titletesterpro.com,https://*.vercel.app,http://localhost:5173
EOF

echo ""
echo "6. Secret Files to add:"
echo "   - Path: firebase-key.json"
echo "   - Content: Your Firebase service account JSON"
echo ""
echo "7. Database & Redis:"
echo "   - Create PostgreSQL database if needed"
echo "   - Create Redis instance if needed"
echo "   - Add their connection URLs to environment variables"
echo ""
echo "8. Click 'Create Web Service'"
echo ""
echo "===================================="
echo ""
echo "After deployment completes, run:"
echo -e "${GREEN}./scripts/verify-ttprov5-deployment.sh https://YOUR-BACKEND-URL.onrender.com${NC}"
echo ""
echo "Then update frontend:"
echo -e "${GREEN}./scripts/update-vercel-env.sh https://YOUR-BACKEND-URL.onrender.com${NC}"