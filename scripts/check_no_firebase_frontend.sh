#!/usr/bin/env bash
set -euo pipefail
echo "Checking for Firebase residue in frontend (src/)..."
PATTERN='(\bfirebase\b|\bfirebase_admin\b|onAuthStateChanged|signInWith|verify_id_token|FIREBASE_)'
if grep -RIn --binary-files=without-match -E "$PATTERN" src/ >/dev/null 2>&1; then
  echo "❌ ERROR: Firebase residue found in frontend."
  echo "Found the following (first 20):"
  grep -RIn --binary-files=without-match -E "$PATTERN" src/ | head -20
  exit 1
fi
echo "✅ [OK] No Firebase references detected in frontend."
