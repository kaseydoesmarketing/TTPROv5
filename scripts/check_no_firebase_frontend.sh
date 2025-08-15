#!/usr/bin/env bash
set -euo pipefail

echo "Checking for Firebase residue in frontend (src/)..."

EXCLUDES=(
  --exclude-dir=node_modules
  --exclude-dir=dist
  --exclude-dir=.next
  --exclude-dir=build
  --exclude-dir=out
  --exclude-dir=coverage
  --exclude-dir=.git
  --exclude-dir=.vercel
  --exclude-dir=.vite
)

EXCLUDE_FILES=(
  --exclude="*.md"
  --exclude="check_no_firebase.sh"
  --exclude="check_no_firebase_frontend.sh"
)

PATTERN='(\bfirebase\b|\bfirebase_admin\b|onAuthStateChanged|signInWith|verify_id_token|FIREBASE_)'

if grep -RIn ${EXCLUDES[@]} ${EXCLUDE_FILES[@]} --binary-files=without-match -E "$PATTERN" src/ >/dev/null 2>&1; then
  echo "❌ ERROR: Firebase residue found in frontend. Remove Firebase references."
  echo "Found the following Firebase references in src/ (showing first 20):"
  grep -RIn ${EXCLUDES[@]} ${EXCLUDE_FILES[@]} --binary-files=without-match -E "$PATTERN" src/ | head -20
  exit 1
fi

echo "✅ [OK] No Firebase references detected in frontend."