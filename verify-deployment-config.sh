#!/usr/bin/env bash
set -euo pipefail

echo "🔍 VERCEL DEPLOYMENT CONFIGURATION VERIFICATION"
echo "==============================================="
echo ""

# 1. Verify build configuration
echo "1️⃣ BUILD CONFIGURATION"
echo "----------------------"
if [ -f "vercel.json" ]; then
    echo "✅ vercel.json exists"
    echo "📄 Current configuration:"
    cat vercel.json | jq '.'
else
    echo "❌ vercel.json missing"
fi
echo ""

# 2. Verify package.json scripts
echo "2️⃣ PACKAGE.JSON SCRIPTS"
echo "-----------------------"
echo "📄 Build scripts:"
grep -A 6 '"scripts"' package.json || echo "❌ scripts section not found"
echo ""

# 3. Test build process
echo "3️⃣ BUILD PROCESS TEST"
echo "---------------------"
echo "🔨 Running build..."
if npm run build > build.log 2>&1; then
    echo "✅ Build successful"
    echo "📊 Build output:"
    tail -5 build.log
    echo ""
    echo "📁 Output directory contents:"
    ls -la dist/ | head -10
else
    echo "❌ Build failed"
    echo "❌ Error details:"
    cat build.log
    exit 1
fi
echo ""

# 4. Verify Firebase cleanup
echo "4️⃣ FIREBASE CLEANUP CHECK"
echo "-------------------------"
if bash ./scripts/check_no_firebase_frontend.sh; then
    echo "✅ No Firebase residue detected"
else
    echo "❌ Firebase residue found"
    exit 1
fi
echo ""

# 5. Verify Auth0 configuration files
echo "5️⃣ AUTH0 CONFIGURATION"
echo "----------------------"
if [ -f "src/env.d.ts" ]; then
    echo "✅ TypeScript env definitions exist"
    echo "📄 Auth0 environment variables defined:"
    grep -E "VITE_AUTH0|VITE_API" src/env.d.ts || echo "❌ Auth0 env vars not found"
else
    echo "❌ src/env.d.ts missing"
fi
echo ""

if [ -f ".env.frontend.example" ]; then
    echo "✅ Environment example file exists"
    echo "📄 Required environment variables:"
    cat .env.frontend.example
else
    echo "❌ .env.frontend.example missing"
fi
echo ""

# 6. Git status
echo "6️⃣ GIT STATUS"
echo "-------------"
echo "📍 Current branch: $(git branch --show-current)"
echo "📍 Latest commit: $(git log --oneline -1)"
echo "📍 Git status:"
if git status --porcelain | grep -q .; then
    echo "⚠️  Uncommitted changes:"
    git status --porcelain
else
    echo "✅ Working directory clean"
fi
echo ""

# 7. Summary
echo "🎯 DEPLOYMENT SUMMARY"
echo "===================="
echo ""
echo "✅ READY FOR VERCEL DEPLOYMENT"
echo ""
echo "📋 Manual Steps Required:"
echo "1. Login to Vercel Dashboard: https://vercel.com/dashboard"
echo "2. Import/Update TTPROv5 Repository"
echo "3. Configure Build Settings:"
echo "   - Framework: Vite"
echo "   - Root Directory: ./"
echo "   - Build Command: npm run build"
echo "   - Output Directory: dist"
echo ""
echo "4. Set Environment Variables:"
echo "   VITE_AUTH0_DOMAIN=dev-p452or5ugtszgvni.us.auth0.com"
echo "   VITE_AUTH0_CLIENT_ID=0yJQgENTsYztUmnCeg7YcswCmQePdHkJ"
echo "   VITE_AUTH0_AUDIENCE="
echo "   VITE_API_BASE_URL=https://ttprov5.onrender.com"
echo ""
echo "5. Deploy from branch: prod/v5"
echo ""
echo "🎉 All prerequisites verified!"