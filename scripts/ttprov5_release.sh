set -euo pipefail
BR="fix/ttprov5-auth-prod-$(date +%Y%m%d_%H%M%S)"
git fetch origin
git checkout -B "$BR" origin/bootstrap/v5

# --- Backend patch: /health, CORS, secure cookie, strict debug gate ---
python - <<'PY'
import re
p="app/main.py"
s=open(p,'r',encoding='utf-8').read()

# Add /health if missing
if "/health" not in s:
  s=re.sub(r'(app\s*=\s*FastAPI[^\n]+)\n)', r'\1\n@app.get("/health")\nasync def health():\n    return {"ok": True}\n', s, count=1)

# CORS middleware (env-driven origins, credentials, explicit methods/headers)
s=re.sub(r'app\.add_middleware\([\s\S]*?CORSMiddleware[\s\S]*?\)',"""app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET","POST","PUT","PATCH","DELETE","OPTIONS"],
    allow_headers=["Authorization","Content-Type","X-Requested-With","Accept"],
)""", s, count=1)

# Debug endpoints must use settings flag (not raw env)
s=re.sub(r'if\s+not\s+os\.getenv\("FIREBASE_DEBUG"[^\)]*\)\s*==\s*"1"\s*:', 'if not settings.is_debug_mode:', s)

# Standardize Set-Cookie attributes for session cookie
s=re.sub(r'response\.set_cookie\([^\)]*\)',"""response.set_cookie(
    key="session_token",
    value=session_jwt if "session_jwt" in globals() else token,
    httponly=True,
    secure=True,
    samesite="none",
    domain=".titletesterpro.com",
    max_age=604800
)""", s)

open(p,'w',encoding='utf-8').write(s)
print("patched", p)
PY

# --- Frontend best-effort: send { id_token } and include credentials on fetches ---
for f in $(git ls-files | grep -E 'src/.*(auth|api|http|login|session).*(ts|tsx|js)$' || true); do
  sed -i.bak -E "s/fetch\(([^,]+),\s*\{([^}]*)\}\)/fetch(\1, {\2, credentials: 'include'})/g" "$f" || true
  sed -i.bak -E "s/\"idToken\"/\"id_token\"/g" "$f" || true
  sed -i.bak -E "s/idToken\s*:/id_token:/g" "$f" || true
  rm -f "$f.bak"
done

# --- Remove Railway leftovers (Render-only) ---
git rm -rf .railway 2>/dev/null || true
git rm -f railway.json 2>/dev/null || true

# --- Commit & push ---
git add -A
git commit -m "auth: fix CORS+cookie+request; add /health; strict debug; purge railway"
git push -u origin "$BR"

echo
echo "===== BRANCH URL ====="
echo "https://github.com/kaseydoesmarketing/TTPROv5/tree/$BR"
echo "======================"
