#!/usr/bin/env bash
set -euo pipefail

echo "Checking for Firebase residue..."

# Directories to ignore (speed + fewer false positives)
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

# Files to ignore
EXCLUDE_FILES=(
  --exclude="*.md"
  --exclude="check_no_firebase.sh"
)

# Regex of things we consider "Firebase residue"
# Using word boundaries for firebase/firebase_admin to reduce false positives.
PATTERN='(\bfirebase\b|\bfirebase_admin\b|onAuthStateChanged|signInWith|verify_id_token|FIREBASE_)'

# First pass: quiet check to decide pass/fail (no binary output)
if grep -RIn ${EXCLUDES[@]} ${EXCLUDE_FILES[@]} --binary-files=without-match -E "$PATTERN" . >/dev/null 2>&1; then
  echo "❌ ERROR: Firebase residue found. Remove Firebase references."
  echo "Found the following Firebase references (showing first 20):"
  grep -RIn ${EXCLUDES[@]} ${EXCLUDE_FILES[@]} --binary-files=without-match -E "$PATTERN" . | head -20
  exit 1
fi

echo "✅ [OK] No Firebase references detected."