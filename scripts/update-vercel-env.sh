#!/bin/bash
# Script to update Vercel environment variables for TTPROv5

set -euo pipefail

# Configuration
VERCEL_TOKEN="${VERCEL_TOKEN:-pTlRlJaadobG5ZwoHUzjFoUb}"
VERCEL_SCOPE="${VERCEL_SCOPE:-ttpro-live}"

# New Backend URL (update this after Render deployment)
NEW_BACKEND_URL="${1:-https://ttprov5-api.onrender.com}"

echo "🚀 Updating Vercel Environment Variables for TTPROv5"
echo "===================================================="
echo "Backend URL: $NEW_BACKEND_URL"
echo ""

# Function to set environment variable for all environments
set_env_var() {
    local NAME="$1"
    local VALUE="$2"
    echo "Setting $NAME..."
    
    for ENV in production preview development; do
        echo "$VALUE" | vercel env add "$NAME" "$ENV" --token "$VERCEL_TOKEN" --scope "$VERCEL_SCOPE" --force 2>/dev/null || true
    done
}

# Update backend URL
set_env_var "NEXT_PUBLIC_API_BASE_URL" "$NEW_BACKEND_URL"

# Ensure Firebase variables are set (using existing values)
set_env_var "NEXT_PUBLIC_FIREBASE_API_KEY" "AIzaSyA8hjvKfC_D1rQqIWgjhxq-xM1cmgDB3z4"
set_env_var "NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN" "titletesterpro.firebaseapp.com"
set_env_var "NEXT_PUBLIC_FIREBASE_PROJECT_ID" "titletesterpro"

# Optional: Stripe public key (if used)
# set_env_var "NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY" "pk_test_..."

echo ""
echo "✅ Environment variables updated successfully!"
echo ""
echo "Next steps:"
echo "1. Deploy frontend: vercel --prod --token $VERCEL_TOKEN --scope $VERCEL_SCOPE"
echo "2. Test authentication flow at https://titletesterpro.com/app"