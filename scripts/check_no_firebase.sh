#!/usr/bin/env bash
set -e
if grep -RIn --exclude-dir=node_modules --exclude-dir=dist --exclude-dir=.next -E "(firebase|firebase_admin|onAuthStateChanged|signInWith|verify_id_token|FIREBASE_)" src app 2>/dev/null; then
  echo "ERROR: Firebase residue found. Remove all Firebase references."
  exit 1
fi
echo "[OK] No Firebase references detected." 